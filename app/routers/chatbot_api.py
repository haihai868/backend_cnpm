from typing import List

from fastapi import APIRouter, Depends
from app import schemas, models, security
from app.services import chatbot_service

router = APIRouter(
    prefix='/chatbot',
    tags=['chatbot']
)

@router.post('/ask', response_model=List[schemas.ChatbotResponse])
def ask_question(request: schemas.ChatbotRequest, user: models.User = Depends(security.get_current_user)):
    return chatbot_service.ask_question(request, user)