from pydantic import BaseModel

class ChatbotRequest(BaseModel):
    question: str

class ChatbotResponse(BaseModel):
    role: str
    content: str