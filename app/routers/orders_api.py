from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import schemas, models
from app.database_connect import get_db

router = APIRouter(
    prefix='/orders',
    tags=['orders']
)

@router.get('/', response_model=List[schemas.OrderOut])
def get_all_orders(db: Session = Depends(get_db)):
    orders = db.query(models.Order).all()
    return orders

@router.get('/{id}', response_model=schemas.OrderOut)
def get_order_by_id(id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == id).first()
    return order



@router.post('/', response_model=schemas.OrderOut)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    new_order = models.Order(**order.model_dump())
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order