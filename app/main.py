from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app import models
from app.database_connect import engine
from app.routers import products_api, users_api, categories_api

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

@app.get('/')
def test_get():
    return {'data': 'test data'}

# uvicorn.run(app, host="0.0.0.0", port=8000)