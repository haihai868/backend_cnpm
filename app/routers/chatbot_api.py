from typing import List

from fastapi import APIRouter, Depends
from app import schemas, models, security
from chatbot.real_main_agent import graph, role

router = APIRouter(
    prefix='/chatbot',
    tags=['chatbot']
)

@router.post('/ask', response_model=List[schemas.ChatbotResponse])
def ask_question(request: schemas.ChatbotRequest, user: models.User = Depends(security.get_current_user)):
    config = {"configurable": {"thread_id": str(user.id)}}

    res = graph.invoke({"user_id": str(user.id) ,"messages": request.question}, config)

    return [{"role": role(m), "content": m.content} for m in res["messages"]]