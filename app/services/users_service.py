import random
import smtplib
from email.message import EmailMessage
from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import schemas, security, models
from app.config import settings
from app.repositories import users_repository


def send_otp(receiver_email: schemas.EmailSchema):
    otp = str(random.randint(100000, 999999))
    mess = EmailMessage()
    mess['Subject'] = 'OTP'
    mess['From'] = settings.email_username
    mess['To'] = receiver_email.email
    mess.set_content(f'Your OTP is {otp}')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(settings.email_username, settings.email_password)
        smtp.send_message(mess)

    return {"otp": otp}


def create_user(user: schemas.UserCreate, db: Session):
    if users_repository.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail='Email already registered')

    user.password = security.hash(user.password)
    return users_repository.create_user(db, user.model_dump())


def get_all_users(db: Session) -> List[models.User]:
    return users_repository.get_all_users(db)


def get_user(db: Session, id: int) -> models.User:
    user = users_repository.get_user_by_id(db, id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return user


def verify_password(password: str, user: models.User):
    if security.verify(password, user.password):
        return {'message': 'Password is correct'}
    raise HTTPException(status_code=403, detail='Incorrect password')


def update_user(updated_user: schemas.UserCreate, db: Session, current_user: models.User):
    updated_user.password = security.hash(updated_user.password)
    res = users_repository.update_user(db, current_user.id, updated_user.model_dump())
    if not res:
        raise HTTPException(status_code=404, detail='User not found')
    return res


def update_user_password(updated_user: schemas.UserUpdatePassword, db: Session):
    updated_user.password = security.hash(updated_user.password)
    res = users_repository.update_user_by_email(db, updated_user.email, updated_user.model_dump())
    if not res:
        raise HTTPException(status_code=404, detail='User not found')
    return res
