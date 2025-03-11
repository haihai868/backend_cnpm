from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas, security
from app.database_connect import get_db

router = APIRouter(
    prefix='/reviews',
    tags=['reviews']
)

@router.get('/')
def get_all_reviews(db: Session = Depends(get_db)):
    return db.query(models.Review).all()

@router.post('/', response_model=schemas.ReviewOut)
def create_review(review: schemas.ReviewCreate, db: Session = Depends(get_db), user: models.User = Depends(security.get_current_user)):
    product = db.query(models.Product).filter(models.Product.id == review.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail='Product not found')

    existed_review = db.query(models.Review).filter(models.Review.product_id == review.product_id,
                                                    models.Review.user_id == user.id).first()
    if existed_review:
        raise HTTPException(status_code=403, detail="You have already reviewed this product")

    review = models.Review(**review.model_dump(), user_id=user.id)
    db.add(review)
    db.commit()
    db.refresh(review)
    return review

@router.get("/{id}", response_model=schemas.ReviewOut)
def get_review(id: int, db: Session = Depends(get_db)):
    review = db.query(models.Review).filter(models.Review.id == id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    return review

@router.delete("/{id}")
def delete_review(id: int, db: Session = Depends(get_db), user: models.User = Depends(security.get_current_user)):
    review = db.query(models.Review).filter(models.Review.id == id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review.user_id != user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own reviews")

    db.delete(review)
    db.commit()
    return {'message': 'Review deleted successfully'}

@router.put("/", response_model=schemas.ReviewOut)
def update_review(review: schemas.ReviewCreate, db: Session = Depends(get_db), user: models.User = Depends(security.get_current_user)):
    review_db = db.query(models.Review).filter(models.Review.product_id == review.product_id,
                                               models.Review.user_id == user.id).first()
    if not review_db:
        raise HTTPException(status_code=404, detail="Review not found")

    review_db.rating = review.rating
    review_db.comment = review.comment
    db.commit()
    db.refresh(review_db)

    return review_db

@router.get('/products/{id}', response_model=List[schemas.ReviewOut])
def get_reviews_by_product_id(id: int, db: Session = Depends(get_db)):
    reviews = db.query(models.Review).filter(models.Review.product_id == id).all()
    return reviews

@router.get('/users/{id}', response_model=List[schemas.ReviewOut])
def get_reviews_by_user_id(id: int, db: Session = Depends(get_db)):
    reviews = db.query(models.Review).filter(models.Review.user_id == id).all()
    return reviews