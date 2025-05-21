import os
from dotenv import load_dotenv

from app.config import settings

load_dotenv()

from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
db = SQLDatabase.from_uri(f"mysql+mysqlconnector://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}")
