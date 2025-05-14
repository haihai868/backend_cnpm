from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import pandas as pd
from pydantic import BaseModel, Field

from chatbot.real_main_agent import graph

df = pd.read_csv("data/question_answer.csv")

questions = df["question"][:3].tolist()
answers = df["answer"][:3].tolist()

print(questions)
print(answers)

judge_llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash",)

class JudgeOutput(BaseModel):
    answer: Literal['correct', 'incorrect'] = Field(
        ...,
        description="Whether the chatbot's answer is correct or not."
    )

judge_llm = judge_llm.with_structured_output(JudgeOutput)

judge_template = """
You are a helpful assistant for a fashion e-commerce website.

You are evaluating a chatbot's answer to a user's question. Your task is to determine whether the chatbot's answer is correct or not.

The chatbot's answer is correct if it has a similar meaning (about 70% match) to the reference answer.

Question:
{question}

Chatbot's answer:
{chatbot_answer}

Reference answer:
{reference_answer}

Answer:
"""

judge_prompt = ChatPromptTemplate.from_template(judge_template)

judge_chain = judge_prompt | judge_llm

for i in range(len(questions)):
    question = questions[i]
    answer = answers[i]

    config = {"configurable": {"thread_id": "1"}}
    res = graph.invoke({"user_id": "1", "messages": question}, config)

    print(res["messages"][-1].content)
    print(judge_chain.invoke({"question": question, "chatbot_answer": res["messages"][-1].content, "reference_answer": answer}))
    print("--------------------------------------------------")