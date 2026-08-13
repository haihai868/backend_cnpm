from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas, security
from app.services import reviews_service
from app.database_connect import get_db

router = APIRouter(
    prefix='/reviews',
    tags=['reviews']
)

@router.get('/', response_model=List[schemas.ReviewAllOut])
def get_all_reviews(db: Session = Depends(get_db)):
    return reviews_service.get_all_reviews(db)

@router.post('/', status_code=201, response_model=schemas.ReviewOut)
def create_review(review: schemas.ReviewCreate, db: Session = Depends(get_db), user: models.User = Depends(security.get_current_user)):
    return reviews_service.create_review(review, db, user)

@router.get("/{id}", response_model=schemas.ReviewOut)
def get_review(id: int, db: Session = Depends(get_db)):
    return reviews_service.get_review(db, id)

@router.delete("/{id}")
def delete_review(id: int, db: Session = Depends(get_db), user: models.User = Depends(security.get_current_user)):
    return reviews_service.delete_review(db, id, user)

@router.delete("/admin/{id}")
def delete_user_reviews(id: int, db: Session = Depends(get_db), user: models.Admin = Depends(security.get_current_admin)):
    return reviews_service.delete_user_reviews_admin(db, id)

@router.put("/", response_model=schemas.ReviewOut)
def update_review(review: schemas.ReviewCreate, db: Session = Depends(get_db), user: models.User = Depends(security.get_current_user)):
    return reviews_service.update_review(review, db, user)

@router.get('/products/{id}', response_model=List[schemas.ReviewOut])
def get_reviews_by_product_id(id: int, db: Session = Depends(get_db)):
    return reviews_service.get_reviews_by_product_id(id, db)

@router.get('/users/{id}', response_model=List[schemas.ReviewOut])
def get_reviews_by_user_id(id: int, db: Session = Depends(get_db)):
    return reviews_service.get_reviews_by_user_id(id, db)