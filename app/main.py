from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app import models
from app.database_connect import engine
from app.routers import products_api, users_api, categories_api, reviews_api, notifications_api, orders_api, authentication, chatbot_api, admins_api

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ['http:/localhost:3000']

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products_api.router)
app.include_router(users_api.router)
app.include_router(categories_api.router)
app.include_router(reviews_api.router)
app.include_router(notifications_api.router)
app.include_router(orders_api.router)
app.include_router(authentication.router)
app.include_router(chatbot_api.router)
app.include_router(admins_api.router)

@app.get('/')
def test_get(response: Response, request: Request):
    return {'data': 'test'}

# uvicorn.run(app, host="0.0.0.0", port=8000)