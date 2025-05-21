from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import RemoveMessage, SystemMessage, HumanMessage, AIMessage, BaseMessage, ToolMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel
from typing_extensions import Annotated
import sqlite3

from chatbot.load_data import user_guide_retriever
from chatbot.prompts import classification_prompt, category_2_prompt, category_3_prompt, generate_query_prompt, \
    generate_query_system_prompt
from chatbot.utils import llm, db


class State(MessagesState):
    user_id: str
    question_category: int
    query: str
    query_result: str

class ClassificationOutput(BaseModel):
    category: int

class QueryOutput(BaseModel):
    query: Annotated[str, ..., "Syntactically valid SQL query."]


def role(m: BaseMessage):
    if isinstance(m, SystemMessage):
        return "system"
    elif isinstance(m, HumanMessage):
        return "user"
    elif isinstance(m, AIMessage):
        return "assistant"
    elif isinstance(m, ToolMessage):
        return "tool"
    return "unknown"


tools = SQLDatabaseToolkit(db=db, llm=llm).get_tools()
tool_node = ToolNode(tools)


def classify_question(state: State):
    chain = classification_prompt | llm.with_structured_output(ClassificationOutput)
    result = chain.invoke({"question": state["messages"][-1].content})
    return {"question_category": result.category}

def classify_question_router(state: State):
    if state["question_category"] == 1:
        return {"after_classify_question": "generate_query_and_answer"}
    elif state["question_category"] == 2:
        return {"after_classify_question": "user_guide_answer"}
    elif state["question_category"] == 3:
        return {"after_classify_question": "small_talk_answer"}

def generate_query_and_answer(state: State):
    system_message = {
        "role": "system",
        "content": generate_query_system_prompt.format(
            dialect=db.dialect,
            top_k=20,
            user_id=state["user_id"]
        ),
    }
    llm_with_tools = llm.bind_tools(tools)
    response = llm_with_tools.invoke([system_message] + state["messages"])

    return {"messages": [response]}

def should_continue(state: State):
    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        return {"should_continue": False}
    else:
        return {"should_continue": True}

def user_guide_answer(state: State):
    docs = user_guide_retriever.get_relevant_documents(state["messages"][-1].content)
    chain = category_2_prompt | llm
    chat_history = state['messages'][:-1]

    result = chain.invoke({"chat_history": chat_history, "question": state["messages"][-1].content, "context": "\n".join([doc.page_content for doc in docs])})
    return {"messages": [{"role": "assistant", "content": result.content}]}

def small_talk_answer(state: State):
    chain = category_3_prompt | llm
    chat_history = state['messages'][:-1]

    result = chain.invoke({"chat_history": chat_history, "question": state["messages"][-1].content})
    return {"messages": [{"role": "assistant", "content": result.content}]}

def manage_memory(state: State):
    messages = state["messages"]

    max_messages_len = 20
    delete_messages_len = 10

    print(len(state["messages"]))

    if isinstance(state["messages"][0], SystemMessage):
        max_messages_len = 21
        delete_messages_len = 11

    if len(state["messages"]) >= max_messages_len + 1:
        print("need to remove messages")
        prev_messages = state["messages"][:delete_messages_len]

        prompt_template = """
                Summarize the following conversation history between a user and a fashion e-commerce assistant.
                Focus on key information like:
                - Products or categories the user was interested in
                - Any specific preferences mentioned (sizes, colors, styles)
                - Questions about website features
                - Order-related information

                Conversation:
                """ + "\n".join([f"{role(m)}: {m.content}" for m in prev_messages])

        response = llm.invoke(prompt_template)
        state["messages"].insert(delete_messages_len, {"role": "system", "content": response.content})

        return {"messages": [RemoveMessage(id=m.id) for m in messages[:delete_messages_len]]}

    print("no remove messages")
    return {}


graph_builder = StateGraph(State)
graph_builder.add_node("manage_memory", manage_memory)
graph_builder.add_node("classify_question", classify_question)
graph_builder.add_node("classify_question_router", classify_question_router)

graph_builder.add_node("generate_query_and_answer", generate_query_and_answer)
graph_builder.add_node("should_continue", should_continue)
graph_builder.add_node("tool_node", tool_node)

graph_builder.add_node("user_guide_answer", user_guide_answer)
graph_builder.add_node("small_talk_answer", small_talk_answer)

graph_builder.add_edge(START, "manage_memory")
graph_builder.add_edge("manage_memory", "classify_question")

graph_builder.add_edge("classify_question", "classify_question_router")

graph_builder.add_conditional_edges("classify_question_router",
                                    lambda state: state["after_classify_question"],
                                    {
                                        "generate_query_and_answer": "generate_query_and_answer",
                                        "user_guide_answer": "user_guide_answer",
                                        "small_talk_answer": "small_talk_answer",
                                    })

graph_builder.add_edge("generate_query_and_answer", END)

graph_builder.add_edge("generate_query_and_answer", "should_continue")
graph_builder.add_conditional_edges("should_continue",
                                    lambda state: state["should_continue"],
                                    {
                                        True: "tool_node",
                                        False: END,
                                    })
graph_builder.add_edge("tool_node", "generate_query_and_answer")

graph_builder.add_edge("user_guide_answer", END)
graph_builder.add_edge("small_talk_answer", END)

conn = sqlite3.connect('chat_history.sqlite', check_same_thread=False)
memory = SqliteSaver(conn)

graph = graph_builder.compile(checkpointer=memory)