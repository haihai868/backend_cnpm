from dotenv import load_dotenv

from langchain_community.tools import QuerySQLDatabaseTool
from langchain_core.messages import RemoveMessage, SystemMessage, HumanMessage, AIMessage, BaseMessage
from pydantic import BaseModel
from typing_extensions import Annotated
import sqlite3

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, START, END, MessagesState

from app.config import settings
from chatbot.load_data import user_guide_retriever
from chatbot.prompts import classification_prompt, db_query_prompt, category_1_prompt, category_2_prompt, category_3_prompt

load_dotenv()

db = SQLDatabase.from_uri(f"mysql+mysqlconnector://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}")
executor = QuerySQLDatabaseTool(db=db)

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash",)

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
    else:
        return "unknown"

def classify_question(state: State):
    chain = classification_prompt | llm.with_structured_output(ClassificationOutput)
    result = chain.invoke({"question": state["messages"][-1].content})
    return {"question_category": result.category}

def classify_question_router(state: State):
    if state["question_category"] == 1:
        return {"after_classify_question": "generate_query"}
    elif state["question_category"] == 2:
        return {"after_classify_question": "user_guide_answer"}
    elif state["question_category"] == 3:
        return {"after_classify_question": "small_talk_answer"}

def generate_query(state: State):
    chain = db_query_prompt | llm.with_structured_output(QueryOutput)
    chat_history = state['messages'][:-1]

    table_info = db.get_table_info(table_names=['categories', 'favourites', 'notifications', 'order_details', 'orders', 'products', 'reports', 'reviews', 'sales', 'users'])
    result = chain.invoke({"chat_history": chat_history, "question": state["messages"][-1].content, "schema": table_info, "user_id": state["user_id"]})
    return {"query": result.query}

def sql_query(state: State):
    return {"query_result": executor.invoke(state["query"])}

def product_details_answer(state: State):
    chain = category_1_prompt | llm
    chat_history = state['messages'][:-1]

    query_result = state["query_result"] if state["query_result"] != "" else "no results"
    result = chain.invoke({"chat_history": chat_history, "question": state["messages"][-1].content, "sql_query": state["query"], "query_result": query_result})
    return {"messages": [{"role": "assistant", "content": result.content}]}

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

        prompt_template = "Summarize the following conversation history into a single message:\n\n" + "\n".join([f"{role(m)}: {m.content}" for m in prev_messages])

        response = llm.invoke(prompt_template)
        state["messages"].insert(delete_messages_len, {"role": "system", "content": response.content})

        return {"messages": [RemoveMessage(id=m.id) for m in messages[:delete_messages_len]]}

    print("no remove messages")
    return {}


graph_builder = StateGraph(State)
graph_builder.add_node("manage_memory", manage_memory)
graph_builder.add_node("classify_question", classify_question)
graph_builder.add_node("classify_question_router", classify_question_router)
graph_builder.add_node("generate_query", generate_query)
graph_builder.add_node("sql_query", sql_query)
graph_builder.add_node("product_details_answer", product_details_answer)
graph_builder.add_node("user_guide_answer", user_guide_answer)
graph_builder.add_node("small_talk_answer", small_talk_answer)

graph_builder.add_edge(START, "manage_memory")
graph_builder.add_edge("manage_memory", "classify_question")

graph_builder.add_edge("classify_question", "classify_question_router")

graph_builder.add_conditional_edges("classify_question_router",
                                    lambda state: state["after_classify_question"],
                                    {
                                        "generate_query": "generate_query",
                                        "user_guide_answer": "user_guide_answer",
                                        "small_talk_answer": "small_talk_answer",
                                    })

graph_builder.add_edge("generate_query", "sql_query")
graph_builder.add_edge("sql_query", "product_details_answer")
graph_builder.add_edge("product_details_answer", END)
graph_builder.add_edge("user_guide_answer", END)
graph_builder.add_edge("small_talk_answer", END)

conn = sqlite3.connect('chat_history.sqlite', check_same_thread=False)
memory = SqliteSaver(conn)

graph = graph_builder.compile(checkpointer=memory)