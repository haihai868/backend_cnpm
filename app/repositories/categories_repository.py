from typing import List, Optional
from sqlalchemy.orm import Session

from app import models


def add_category(db: Session, data: dict) -> models.Category:
    category = models.Category(**data)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_all_categories(db: Session) -> List[models.Category]:
    return db.query(models.Category).all()


def get_by_name(db: Session, name: str) -> Optional[models.Category]:
    return db.query(models.Category).filter(models.Category.name == name).first()


def get_by_id(db: Session, id: int) -> Optional[models.Category]:
    return db.query(models.Category).filter(models.Category.id == id).first()
