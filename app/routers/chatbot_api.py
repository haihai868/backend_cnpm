from fastapi import APIRouter
from app import schemas

from chatbot.rag_src.main_chain import answer_question

router = APIRouter(
    prefix='/chatbot',
    tags=['chatbot']
)

@router.post('/ask', response_model=schemas.ChatbotResponse)
def ask_question(request: schemas.ChatbotRequest):
    answer, total_time, retrieval_time, llm_time = answer_question(request.question)
    return {'answer': answer, 'total_time': total_time, 'retrieval_time': retrieval_time, 'llm_time': llm_time}