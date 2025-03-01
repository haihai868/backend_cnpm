from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.database_connect import get_db

router = APIRouter(
    prefix='/categories',
    tags=['categories']
)

@router.post('/', response_model=schemas.CategoryOut)
def add_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    category = models.Category(**category.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@router.get('/')
def get_all_categories(db: Session = Depends(get_db)):
    categories = db.query(models.Category).all()
    return categories