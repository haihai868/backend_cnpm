from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database_connect import get_db

router = APIRouter(
    prefix='/categories',
    tags=['categories']
)

@router.post('/', status_code=201, response_model=schemas.CategoryOut)
def add_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    check_category = db.query(models.Category).filter(models.Category.name == category.name).first()
    if check_category:
        raise HTTPException(status_code=400, detail='Category already exists')

    category = models.Category(**category.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@router.get('/')
def get_all_categories(db: Session = Depends(get_db)):
    categories = db.query(models.Category).all()
    return categories

@router.get('/{name}')
def get_by_name(name: str, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.name == name).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return category

@router.get('/id/{id}')
def get_by_id(id: int, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.id == id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return category