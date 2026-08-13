from typing import List, Optional
from sqlalchemy.orm import Session

from app import models


def get_all_users(db: Session) -> List[models.User]:
    return db.query(models.User).all()


def get_user_by_id(db: Session, id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user_data: dict) -> models.User:
    new_user = models.User(**user_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def update_user(db: Session, user_id: int, data: dict) -> Optional[models.User]:
    q = db.query(models.User).filter(models.User.id == user_id)
    if not q.first():
        return None
    q.update(data, synchronize_session=False)
    db.commit()
    return q.first()


def update_user_by_email(db: Session, email: str, data: dict) -> Optional[models.User]:
    q = db.query(models.User).filter(models.User.email == email)
    if not q.first():
        return None
    q.update(data, synchronize_session=False)
    db.commit()
    return q.first()
