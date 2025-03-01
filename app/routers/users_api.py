from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app import schemas, security, models
from app.database_connect import get_db

router = APIRouter(
    prefix='/users',
    tags=['users']
)

@router.post('/')
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    query = db.query(models.User).filter(models.User.email == user.email)
    if query.first():
        raise HTTPException(status_code=400, detail='Email already registered')

    hashed_pass = security.hash(user.password)
    user.password = hashed_pass
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