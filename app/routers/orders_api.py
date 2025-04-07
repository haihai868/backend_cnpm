from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas, models
from app.database_connect import get_db
from app.schemas import OrderOut
from app.security import get_current_user

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
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')

    return order

@router.post('/', status_code=201, response_model=schemas.OrderOut)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    new_order = models.Order(**order.model_dump())
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

@router.put('/', response_model=schemas.OrderOut)
def add_product_to_order(order_detail: schemas.OrderDetailCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if order_detail.quantity <= 0:
        raise HTTPException(status_code=400, detail='Quantity must be greater than 0')

    order = db.query(models.Order).filter(models.Order.user_id == current_user.id,
                                         models.Order.status == 'Unpaid').first()

    if not order:
        raise HTTPException(status_code=404, detail='Order not found')

    product = db.query(models.Product).filter(models.Product.id == order_detail.product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail='Product not found')

    order_detail = db.query(models.OrderDetail).filter(models.OrderDetail.product_id == order_detail.product_id,
                                                         models.OrderDetail.order_id == order.id).first()
    if order_detail:
        raise HTTPException(status_code=400, detail='Product already in order')
    else:
        order_detail = models.OrderDetail(product_id=order_detail.product_id, order_id=order.id, quantity=order_detail.quantity)
        db.add(order_detail)

    db.commit()
    db.refresh(order)
    return order

@router.get('/users/{id}', response_model=OrderOut)
def get_unpaid_order_by_user_id(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    unpaid_order = db.query(models.Order).filter(models.Order.user_id == id,
                                                 models.Order.status == 'Unpaid').first()

    return unpaid_order

@router.get('/users/{id}', response_model=OrderOut)
def get_paid_order_by_user_id(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    paid_order = db.query(models.Order).filter(models.Order.user_id == id,
                                               models.Order.status == 'Paid').all()

    return paid_order

@router.get('/{id}/total_price')
def get_total_order_price(id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')

    total = 0
    for order_detail in order.order_details:
        total += order_detail.product.price * order_detail.quantity

    return {'order_id': id ,'total': total}

@router.put('/{id}/payment', response_model=schemas.OrderOut)
def pay_order(id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')

    if order.status == 'Paid':
        raise HTTPException(status_code=400, detail='Order already paid')

    order.status = 'Paid'
    db.commit()
    db.refresh(order)
    return order

@router.delete('/{id}')
def delete_product_from_order(product_id: int, order_id: int, db: Session = Depends(get_db)):
    order_detail = db.query(models.OrderDetail).filter(models.OrderDetail.product_id == product_id,
                                                         models.OrderDetail.order_id == order_id).first()
    if not order_detail:
        raise HTTPException(status_code=404, detail='Order detail not found')

    db.delete(order_detail)
    db.commit()
    return {'message': 'Product deleted successfully'}
