from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.services import categories_service
from app.database_connect import get_db

router = APIRouter(
    prefix='/categories',
    tags=['categories']
)

@router.post('/', status_code=201, response_model=schemas.CategoryOut)
def add_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    return categories_service.add_category(category, db)

@router.get('/')
def get_all_categories(db: Session = Depends(get_db)):
    return categories_service.get_all_categories(db)

@router.get('/{name}')
def get_by_name(name: str, db: Session = Depends(get_db)):
    return categories_service.get_by_name(name, db)

@router.get('/id/{id}')
def get_by_id(id: int, db: Session = Depends(get_db)):
    return categories_service.get_by_id(id, db)