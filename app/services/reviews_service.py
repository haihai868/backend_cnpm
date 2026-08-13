from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.repositories import reviews_repository


def get_all_reviews(db: Session) -> List[models.Review]:
    return reviews_repository.get_all_reviews(db)


def create_review(review: schemas.ReviewCreate, db: Session, user: models.User) -> models.Review:
    product = db.query(models.Product).filter(models.Product.id == review.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail='Product not found')

    existed_review = db.query(models.Review).filter(models.Review.product_id == review.product_id,
                                                    models.Review.user_id == user.id).first()
    if existed_review:
        raise HTTPException(status_code=403, detail="You have already reviewed this product")

    review_obj = review.model_dump()
    review_obj.update({'user_id': user.id})
    return reviews_repository.create_review(db, review_obj)


def get_review(db: Session, id: int) -> models.Review:
    review = reviews_repository.get_review_by_id(db, id)
    if not review:
        raise HTTPException(status_code=404, detail='Review not found')
    return review


def delete_review(db: Session, id: int, user: models.User):
    review = reviews_repository.get_review_by_id(db, id)
    if not review:
        raise HTTPException(status_code=404, detail='Review not found')

    if review.user_id != user.id:
        raise HTTPException(status_code=403, detail='You can only delete your own reviews')

    reviews_repository.delete_review(db, id)
    return {'message': 'Review deleted successfully'}


def delete_user_reviews_admin(db: Session, id: int):
    ok = reviews_repository.delete_review(db, id)
    if not ok:
        raise HTTPException(status_code=404, detail='Review not found')
    return {'message': 'Reviews deleted successfully'}


def update_review(review: schemas.ReviewCreate, db: Session, user: models.User):
    updated = reviews_repository.update_review_by_product_and_user(db, review.product_id, user.id, review.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail='Review not found')
    return updated


def get_reviews_by_product_id(id: int, db: Session):
    return reviews_repository.get_reviews_by_product_id(db, id)


def get_reviews_by_user_id(id: int, db: Session):
    return reviews_repository.get_reviews_by_user_id(db, id)
