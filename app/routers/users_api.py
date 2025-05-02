from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import smtplib
import random
from email.message import EmailMessage

from app import schemas, security, models
from app.database_connect import get_db
from app.config import settings

router = APIRouter(
    prefix='/users',
    tags=['users']
)

@router.post('/otp')
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


@router.post('/', status_code=201, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    query = db.query(models.User).filter(models.User.email == user.email)
    if query.first():
        raise HTTPException(status_code=400, detail='Email already registered')

    user.password = security.hash(user.password)
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get('/')
def get_all_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

@router.post("/password-verification/{password}")
def verify_password(password: str, user: models.User = Depends(security.get_current_user)):
    if security.verify(password, user.password):
        return {'message': 'Password is correct'}
    raise HTTPException(status_code=403, detail='Incorrect password')

@router.put("/", response_model=schemas.UserOut)
def update_user(updated_user: schemas.UserCreate, db: Session = Depends(get_db), user: models.User = Depends(security.get_current_user)):
    user_query = db.query(models.User).filter(models.User.id == user.id)
    updated_user.password = security.hash(updated_user.password)
    user_query.update(updated_user.model_dump(), synchronize_session=False)
    db.commit()
    return user_query.first()

@router.put("/password", response_model=schemas.UserOut)
def update_user_password(updated_user: schemas.UserUpdatePassword, db: Session = Depends(get_db), user: models.User = Depends(security.get_current_user)):
    user_query = db.query(models.User).filter(models.User.id == user.id)
    updated_user.password = security.hash(updated_user.password)
    user_query.update(updated_user.model_dump(), synchronize_session=False)
    db.commit()
    return user_query.first()
