from typing import List
from app import schemas, models
from chatbot.real_main_agent import graph, role


def ask_question(request: schemas.ChatbotRequest, user: models.User) -> List[schemas.ChatbotResponse]:
    config = {"configurable": {"thread_id": str(user.id)}}
    res = graph.invoke({"user_id": str(user.id), "messages": request.question}, config)
    return [{"role": role(m), "content": m.content} for m in res["messages"]]
