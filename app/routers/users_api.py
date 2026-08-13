from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import smtplib
import random
from email.message import EmailMessage

from app import schemas, security, models
from app.services import users_service
from app.database_connect import get_db
from app.config import settings

router = APIRouter(
    prefix='/users',
    tags=['users']
)

@router.post('/otp')
def send_otp(receiver_email: schemas.EmailSchema):
    return users_service.send_otp(receiver_email)


@router.post('/', status_code=201, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return users_service.create_user(user, db)

@router.get('/')
def get_all_users(db: Session = Depends(get_db)):
    return users_service.get_all_users(db)


@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    return users_service.get_user(db, id)

@router.post("/password-verification/{password}")
def verify_password(password: str, user: models.User = Depends(security.get_current_user)):
    return users_service.verify_password(password, user)

@router.put("/", response_model=schemas.UserOut)
def update_user(updated_user: schemas.UserCreate, db: Session = Depends(get_db), user: models.User = Depends(security.get_current_user)):
    return users_service.update_user(updated_user, db, user)

@router.put("/password", response_model=schemas.UserOut)
def update_user_password(updated_user: schemas.UserUpdatePassword, db: Session = Depends(get_db)):
    return users_service.update_user_password(updated_user, db)
