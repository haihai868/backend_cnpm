import os
from dotenv import load_dotenv
import time

from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

persistent_dir = os.path.join(os.path.dirname(__file__), "vstores")

embedding_function = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-exp-03-07")

if not os.path.exists(persistent_dir):
    loader = TextLoader("data/User_Guide.txt", encoding="utf-8")
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    documents = text_splitter.split_documents(docs)

    db = Chroma(
        collection_name="user_guide",
        embedding_function = embedding_function,
        persist_directory=persistent_dir,
    )


    def chunked(iterable, size):
        for i in range(0, len(iterable), size):
            yield iterable[i:i + size]


    for batch in chunked(documents, 5):
        db.add_documents(batch)
        time.sleep(100)

user_guide_db = Chroma(
    collection_name="user_guide",
    embedding_function = embedding_function,
    persist_directory=persistent_dir,
)

user_guide_retriever = user_guide_db.as_retriever(search_kwargs={"k": 3})