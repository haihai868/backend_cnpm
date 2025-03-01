from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models, security
from app.database_connect import get_db

router = APIRouter(
    prefix='/authentication',
    tags=['authentication']
)

@router.post('/login')
def login(form_data: OAuth2PasswordRequestForm, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()

    if not user or not security.verify(form_data.password, user.password):
        raise HTTPException(status_code=400, detail='Incorrect email or password')

    return {'access_token': security.create_access_token(data={'sub': user.email})}