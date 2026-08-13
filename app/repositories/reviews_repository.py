from typing import List, Optional
from sqlalchemy.orm import Session

from app import models


def get_all_reviews(db: Session) -> List[models.Review]:
    return db.query(models.Review).all()


def get_review_by_id(db: Session, id: int) -> Optional[models.Review]:
    return db.query(models.Review).filter(models.Review.id == id).first()


def create_review(db: Session, review_data: dict) -> models.Review:
    review = models.Review(**review_data)
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def delete_review(db: Session, id: int):
    review = db.query(models.Review).filter(models.Review.id == id).first()
    if not review:
        return False
    db.delete(review)
    db.commit()
    return True


def get_reviews_by_product_id(db: Session, id: int):
    return db.query(models.Review).filter(models.Review.product_id == id).all()


def get_reviews_by_user_id(db: Session, id: int):
    return db.query(models.Review).filter(models.Review.user_id == id).all()


def update_review_by_product_and_user(db: Session, product_id: int, user_id: int, data: dict) -> Optional[models.Review]:
    review = db.query(models.Review).filter(models.Review.product_id == product_id,
                                           models.Review.user_id == user_id).first()
    if not review:
        return None
    review.rating = data.get('rating', review.rating)
    review.comment = data.get('comment', review.comment)
    db.commit()
    db.refresh(review)
    return review
