from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas, security
from app.services import sales_service
from app.database_connect import get_db

router = APIRouter(
    prefix='/sales',
    tags=['sales']
)

@router.get('/', response_model=List[schemas.SaleOut])
def get_all_sales(db: Session = Depends(get_db)):
    return sales_service.get_all_sales(db)

@router.get('/{id}', response_model=schemas.SaleOut)
def get_sale_by_id(id: int, db: Session = Depends(get_db)):
    return sales_service.get_sale_by_id(id, db)

@router.post('/', status_code=201, response_model=schemas.SaleOut)
def create_sale(sale: schemas.SaleCreate, db: Session = Depends(get_db), admin: models.Admin = Depends(security.get_current_admin)):
    return sales_service.create_sale(sale, db, admin)

@router.put('/{id}', response_model=schemas.SaleOut)
def end_sale(id: int, db: Session = Depends(get_db), admin: models.Admin = Depends(security.get_current_admin)):
    return sales_service.end_sale(id, db, admin)
