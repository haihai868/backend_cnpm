import time

import httpx
from langchain_core.prompts import ChatPromptTemplate

from chatbot.rag_src.utils import llm
from chatbot.rag_src.astradb_retrievers import prods_retriever, faqs_retriever
from chatbot.rag_src.question_classification_chain import classify_question

template = """
You are a helpful customer support assistant for a fashion e-commerce website. Answer the user's question based on the provided information. If you don't know the answer, just say that you don't have enough information.

This question is about: {category_description}

{context}

User question: {question}

Answer:
"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | llm

def answer_question(question: str) -> tuple[str, float, float, float]:
    start_time = time.time()

    # Classify the question
    try :
        question_category = classify_question(question)
        if question_category not in ["1", "2", "3", "4"]:
            return "False classification", 0, 0, 0
    except httpx.HTTPStatusError:
        return "", 0, 0, 0

    # Time the retrieval step
    retrieval_start = time.time()

    # context = ""
    # category_description = ""

    if question_category == "1":
        products = prods_retriever.invoke(question)
        context = f"Relevant product details:\n{products}"
        category_description = "Product information and details"

        print("Category: Product information and details")
    elif question_category == "2":
        faqs = faqs_retriever.invoke(question)
        context = f"Relevant FAQ details:\n{faqs}"
        category_description = "Website usage and features"

        print("Category: Website usage and features")
    elif question_category == "3":
        products = prods_retriever.invoke(question)
        faqs = faqs_retriever.invoke(question)
        context = f"Relevant product details:\n{products}\n\nRelevant FAQ details:\n{faqs}"
        category_description = "Both product information and website usage"

        print("Category: Both product information and website usage")
    else:
        context = "No relevant information found, answer in a general way"
        category_description = "Irrelevant question"

    retrieval_time = time.time() - retrieval_start

    # Time the LLM response step
    llm_start = time.time()
    try:
        result = chain.invoke({
            "category_description": category_description,
            "context": context,
            "question": question
        })
    except httpx.HTTPStatusError:
        return "", 0, 0, 0

    llm_time = time.time() - llm_start
    total_time = time.time() - start_time
    return result.content, total_time, retrieval_time, llm_time
