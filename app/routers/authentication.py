from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models, security
from app.services import authentication_service
from app.database_connect import get_db

router = APIRouter(
    tags=['authentication']
)

@router.post('/admin-login')
def admin_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return authentication_service.admin_login(form_data, db)

@router.post('/login')
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return authentication_service.login(form_data, db)