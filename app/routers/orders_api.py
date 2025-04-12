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

@router.get('/products', response_model=List[schemas.ProductOut])
def get_products_in_order(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    order = db.query(models.Order).filter(models.Order.user_id == user.id,
                                         models.Order.status == 'Unpaid').first()
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')

    products = [order_detail.product for order_detail in order.order_details]
    print(products)
    return products

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

@router.put('/', response_model=schemas.OrderDetailOut)
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

    order.status = 'Paid'
    db.commit()
    db.refresh(order)
    return order


