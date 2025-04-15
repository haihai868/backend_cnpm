from pydantic import BaseModel

class ChatbotRequest(BaseModel):
    question: str

class ChatbotResponse(BaseModel):
    answer: str
    total_time: float
    retrieval_time: float
    llm_time: float