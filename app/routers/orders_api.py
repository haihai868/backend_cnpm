from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas, models
from app.services import orders_service
from app.database_connect import get_db
from app.schemas import OrderOut
from app.security import get_current_user, get_current_admin

router = APIRouter(
    prefix='/orders',
    tags=['orders']
)

@router.get('/', response_model=List[schemas.OrderOut])
def get_all_orders(db: Session = Depends(get_db)):
    return orders_service.get_all_orders(db)

@router.get('/products/sale_quantity', response_model=List[schemas.ProductWithPaidQuantity])
def get_sale_quantity(db: Session = Depends(get_db)):
    return orders_service.get_sale_quantity(db)

@router.get('/products', response_model=List[schemas.ProductOrderOut])
def get_products_in_order(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return orders_service.get_products_in_order(db, user)

@router.get('/{order_id}/products', response_model=List[schemas.ProductOrderOut])
def get_products_in_order_by_id(order_id: int, db: Session = Depends(get_db)):
    return orders_service.get_products_in_order_by_id(order_id, db)

@router.get('/{id}', response_model=schemas.OrderOut)
def get_order_by_id(id: int, db: Session = Depends(get_db)):
    return orders_service.get_order_by_id(id, db)

@router.post('/', status_code=201, response_model=schemas.OrderOut)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    return orders_service.create_order(order, db)

@router.put('/', response_model=schemas.OrderOut)
def update_order(order: schemas.OrderCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return orders_service.update_order(order, db, user)

@router.put('/product', response_model=schemas.OrderDetailOut)
def add_product_to_order(order_detail_create: schemas.OrderDetailCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return orders_service.add_product_to_order(order_detail_create, db, current_user)

@router.delete('/{product_id}')
def delete_product_from_order(product_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return orders_service.delete_product_from_order(product_id, db, user)

@router.get('/users/{id}', response_model=List[OrderOut])
def get_orders_by_user_id(id: int, db: Session = Depends(get_db), status: str = 'All'):
    return orders_service.get_orders_by_user_id(id, db, status)

@router.get('/{id}/total_price')
def get_total_order_price(id: int, db: Session = Depends(get_db)):
    return orders_service.get_total_order_price(id, db)

@router.put('/payment', response_model=schemas.OrderOut)
def pay_order(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return orders_service.pay_order(db, user)

@router.put('/payment/confirmation/{order_id}', response_model=schemas.OrderOut)
def comfirm_payment(order_id: int, db: Session = Depends(get_db), admin: models.Admin = Depends(get_current_admin)):
    return orders_service.confirm_payment(order_id, db)

@router.delete('/payment/user/cancelation/{order_id}')
def user_cancel_payment(order_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return orders_service.user_cancel_payment(order_id, db, user)

@router.delete('/payment/admin/cancelation/{order_id}')
def admin_cancel_payment(order_id: int, db: Session = Depends(get_db), admin: models.Admin = Depends(get_current_admin)):
    return orders_service.admin_cancel_payment(order_id, db)

