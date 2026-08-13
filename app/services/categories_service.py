from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import schemas, models
from app.repositories import categories_repository


def add_category(category: schemas.CategoryCreate, db: Session):
    if categories_repository.get_by_name(db, category.name):
        raise HTTPException(status_code=400, detail='Category already exists')
    return categories_repository.add_category(db, category.model_dump())


def get_all_categories(db: Session) -> List[models.Category]:
    return categories_repository.get_all_categories(db)


def get_by_name(name: str, db: Session) -> models.Category:
    category = categories_repository.get_by_name(db, name)
    if not category:
        raise HTTPException(status_code=404, detail='Category not found')
    return category


def get_by_id(id: int, db: Session) -> models.Category:
    category = categories_repository.get_by_id(db, id)
    if not category:
        raise HTTPException(status_code=404, detail='Category not found')
    return category
