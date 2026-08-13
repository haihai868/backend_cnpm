from fastapi.security import OAuth2PasswordRequestForm
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models, security


def admin_login(form_data: OAuth2PasswordRequestForm, db: Session):
    admin = db.query(models.Admin).filter(models.Admin.email == form_data.username).first()
    if not admin or not security.verify(form_data.password, admin.password):
        raise HTTPException(status_code=403, detail='Incorrect username or password')

    access_token = security.create_access_token(data={'user_email': admin.email, 'user_id': admin.id})
    return {'access_token': access_token, 'token_type': 'bearer'}


def login(form_data: OAuth2PasswordRequestForm, db: Session):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()

    if not user or not security.verify(form_data.password, user.password):
        raise HTTPException(status_code=403, detail='Incorrect email or password')

    access_token = security.create_access_token(data={'user_email': user.email, 'user_id': user.id})
    return {'access_token': access_token, 'token_type': 'bearer'}
