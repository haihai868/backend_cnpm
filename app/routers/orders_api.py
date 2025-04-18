from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas, models
from app.database_connect import get_db
from app.schemas import OrderOut
from app.security import get_current_user, get_current_admin

router = APIRouter(
    prefix='/orders',
    tags=['orders']
)

@router.get('/', response_model=List[schemas.OrderOut])
def get_all_orders(db: Session = Depends(get_db)):
    orders = db.query(models.Order).all()
    return orders

@router.get('/products', response_model=List[schemas.ProductOrderOut])
def get_products_in_order(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    order = db.query(models.Order).filter(models.Order.user_id == user.id,
                                         models.Order.status == 'Unpaid').first()
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')

    order_details = db.query(models.OrderDetail).filter(models.OrderDetail.order_id == order.id).all()
    products_with_quantity = [schemas.ProductOrderOut(**order_detail.product.__dict__, quantity_in_order=order_detail.quantity) for order_detail in order_details]
    return products_with_quantity

@router.get('/{order_id}/products', response_model=List[schemas.ProductOrderOut])
def get_products_in_order_by_id(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')

    order_details = db.query(models.OrderDetail).filter(models.OrderDetail.order_id == order.id).all()
    products_with_quantity = [schemas.ProductOrderOut(**order_detail.product.__dict__, quantity_in_order=order_detail.quantity) for order_detail in order_details]
    return products_with_quantity

@router.get('/{id}', response_model=schemas.OrderOut)
def get_order_by_id(id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')

    return order

@router.post('/', status_code=201, response_model=schemas.OrderOut)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    order_query = db.query(models.Order).filter(models.Order.user_id == order.user_id,
                                                models.Order.status == 'Unpaid').first()
    if order_query:
        raise HTTPException(status_code=400, detail='User already has an unpaid order')

    new_order = models.Order(**order.model_dump())
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

@router.put('/', response_model=schemas.OrderOut)
def update_order(order: schemas.OrderCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    if order.user_id != user.id:
        raise HTTPException(status_code=403, detail='You can only update your own order')

    order_query = db.query(models.Order).filter(models.Order.user_id == order.user_id,
                                                models.Order.status == 'Unpaid')
    if not order_query:
        raise HTTPException(status_code=404, detail='Order not found')

    order_query.update(order.model_dump(), synchronize_session=False)
    db.commit()
    return order_query.first()

@router.put('/product', response_model=schemas.OrderDetailOut)
def add_product_to_order(order_detail_create: schemas.OrderDetailCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if order_detail_create.quantity <= 0:
        raise HTTPException(status_code=400, detail='Quantity must be greater than 0')

    order = db.query(models.Order).filter(models.Order.user_id == current_user.id,
                                         models.Order.status == 'Unpaid').first()

    if not order:
        raise HTTPException(status_code=404, detail='Order not found')

    product = db.query(models.Product).filter(models.Product.id == order_detail_create.product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail='Product not found')

    order_detail = db.query(models.OrderDetail).filter(models.OrderDetail.product_id == order_detail_create.product_id,
                                                         models.OrderDetail.order_id == order.id).first()
    if order_detail:
        raise HTTPException(status_code=400, detail='Product already in order')
    else:
        order_detail = models.OrderDetail(product_id=order_detail_create.product_id, order_id=order.id, quantity=order_detail_create.quantity,
                                          priceEach=product.price if order_detail_create.priceEach is None else order_detail_create.priceEach)
        db.add(order_detail)

    db.commit()
    db.refresh(order_detail)
    return order_detail

@router.delete('/{product_id}')
def delete_product_from_order(product_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    order = db.query(models.Order).filter(models.Order.user_id == user.id,
                                         models.Order.status == 'Unpaid').first()

    if not order:
        raise HTTPException(status_code=404, detail='Order not found')

    order_detail = db.query(models.OrderDetail).filter(models.OrderDetail.product_id == product_id,
                                                         models.OrderDetail.order_id == order.id).first()
    if not order_detail:
        raise HTTPException(status_code=404, detail="Product not in user's order")

    db.delete(order_detail)
    db.commit()
    return {'message': 'Product deleted successfully'}

@router.get('/users/{id}', response_model=List[OrderOut])
def get_orders_by_user_id(id: int, db: Session = Depends(get_db), status: str = 'All'):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    if status == 'All':
        orders = db.query(models.Order).filter(models.Order.user_id == id).all()
        return orders

    if status == 'Pending':
        pending_order = db.query(models.Order).filter(models.Order.user_id == id,
                                                   models.Order.status == 'Pending').all()

        return pending_order

    if status == 'Paid':
        paid_order = db.query(models.Order).filter(models.Order.user_id == id,
                                                   models.Order.status == 'Paid').all()

        return paid_order

    unpaid_order = db.query(models.Order).filter(models.Order.user_id == id,
                                                 models.Order.status == 'Unpaid').all()

    return unpaid_order

@router.get('/{id}/total_price')
def get_total_order_price(id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')

    total = 0
    for order_detail in order.order_details:
        total += order_detail.product.price * order_detail.quantity

    return {'order_id': id ,'total': total}

@router.put('/payment', response_model=schemas.OrderOut)
def pay_order(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    order = db.query(models.Order).filter(models.Order.user_id == user.id,
                                         models.Order.status == 'Unpaid').first()
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')

    for order_detail in order.order_details:
        if order_detail.product.quantity_in_stock < order_detail.quantity:
            raise HTTPException(status_code=400, detail=f'Not enough product {order_detail.product.name} in stock')

    order.status = 'Pending'
    order.started_payment_at = datetime.now()
    for order_detail in order.order_details:
        order_detail.product.quantity_in_stock -= order_detail.quantity

    db.commit()
    db.refresh(order)
    return order

@router.put('/payment/confirmation/{order_id}', response_model=schemas.OrderOut)
def comfirm_payment(order_id: int, db: Session = Depends(get_db), admin: models.Admin = Depends(get_current_admin)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail='Order not found')

    if order.status != 'Pending':
        raise HTTPException(status_code=400, detail='Order is not pending')

    order.status = 'Paid'
    order.confirmed_at = datetime.now()
    db.commit()
    db.refresh(order)
    return order

@router.delete('/payment/cancelation/{order_id}')
def user_cancel_payment(order_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')

    if order.user_id != user.id:
        raise HTTPException(status_code=403, detail='You can only cancel your own order')

    if order.status != 'Pending':
        raise HTTPException(status_code=400, detail='Order is not pending')

    for order_detail in order.order_details:
        order_detail.product.quantity_in_stock += order_detail.quantity
        db.delete(order_detail)

    db.delete(order)
    db.commit()
    return {'message': 'Order canceled successfully'}

@router.delete('/payment/user/cancelation/{order_id}')
def user_cancel_payment(order_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')

    if order.user_id != user.id:
        raise HTTPException(status_code=403, detail='You can only cancel your own order')

    if order.status != 'Pending':
        raise HTTPException(status_code=400, detail='Order is not pending')

    for order_detail in order.order_details:
        order_detail.product.quantity_in_stock += order_detail.quantity
        db.delete(order_detail)

    db.delete(order)
    db.commit()
    return {'message': 'Order canceled successfully'}

@router.delete('/payment/admin/cancelation/{order_id}')
def admin_cancel_payment(order_id: int, db: Session = Depends(get_db), admin: models.Admin = Depends(get_current_admin)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')

    if order.status != 'Pending':
        raise HTTPException(status_code=400, detail='Order is not pending')

    for order_detail in order.order_details:
        order_detail.product.quantity_in_stock += order_detail.quantity
        db.delete(order_detail)

    db.delete(order)
    db.commit()
    return {'message': 'Order canceled successfully'}