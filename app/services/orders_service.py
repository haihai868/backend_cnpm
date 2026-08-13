from datetime import datetime
from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import schemas, models
from app.repositories import orders_repository


def get_all_orders(db: Session) -> List[models.Order]:
    return orders_repository.get_all_orders(db)


def get_sale_quantity(db: Session):
    order_details = orders_repository.get_sale_quantity(db)
    products = {}

    for order_detail in order_details:
        product = order_detail.product
        if product.name not in products:
            products[product.name] = {'paid_quantity': order_detail.quantity, 'price': product.price, 'image': product.image}
        else:
            products[product.name]['paid_quantity'] += order_detail.quantity

    products = [{'name': name, 'paid_quantity': data['paid_quantity'], 'price': data['price'], 'image': data['image']} for name, data in products.items()]
    return products


def get_products_in_order(db: Session, user: models.User):
    order = orders_repository.get_unpaid_order_by_user(db, user.id)
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')

    order_details = order.order_details
    products_with_quantity = [schemas.ProductOrderOut(**od.product.__dict__, quantity_in_order=od.quantity) for od in order_details]
    return products_with_quantity


def get_products_in_order_by_id(order_id: int, db: Session):
    order = orders_repository.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')
    order_details = order.order_details
    products_with_quantity = [schemas.ProductOrderOut(**od.product.__dict__, quantity_in_order=od.quantity) for od in order_details]
    return products_with_quantity


def get_order_by_id(id: int, db: Session):
    order = orders_repository.get_order_by_id(db, id)
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')
    return order


def create_order(order: schemas.OrderCreate, db: Session):
    order_query = orders_repository.get_unpaid_order_by_user(db, order.user_id)
    if order_query:
        raise HTTPException(status_code=400, detail='User already has an unpaid order')
    return orders_repository.create_order(db, order.model_dump())


def update_order(order: schemas.OrderCreate, db: Session, user: models.User):
    if order.user_id != user.id:
        raise HTTPException(status_code=403, detail='You can only update your own order')

    updated = orders_repository.update_order(db, order.user_id, order.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail='Order not found')
    return updated


def add_product_to_order(order_detail_create: schemas.OrderDetailCreate, db: Session, current_user: models.User):
    if order_detail_create.quantity <= 0:
        raise HTTPException(status_code=400, detail='Quantity must be greater than 0')

    order = orders_repository.get_unpaid_order_by_user(db, current_user.id)
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')

    product = db.query(models.Product).filter(models.Product.id == order_detail_create.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail='Product not found')

    od = orders_repository.add_order_detail(db, order.id, order_detail_create.product_id, order_detail_create.quantity, product.price, order_detail_create.priceEach)
    if od is None:
        raise HTTPException(status_code=400, detail='Product already in order')
    return od


def delete_product_from_order(product_id: int, db: Session, user: models.User):
    order = orders_repository.get_unpaid_order_by_user(db, user.id)
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')

    ok = orders_repository.delete_order_detail(db, product_id, order.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Product not in user's order")
    return {'message': 'Product deleted successfully'}


def get_orders_by_user_id(id: int, db: Session, status: str = 'All'):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return orders_repository.get_orders_by_user_and_status(db, id, status)


def get_total_order_price(id: int, db: Session):
    total = orders_repository.calculate_total(db, id)
    if total is None:
        raise HTTPException(status_code=404, detail='Order not found')
    return {'order_id': id, 'total': total}


def pay_order(db: Session, user: models.User):
    order = orders_repository.get_unpaid_order_by_user(db, user.id)
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')

    for od in order.order_details:
        if od.product.quantity_in_stock < od.quantity:
            raise HTTPException(status_code=400, detail=f'Not enough product {od.product.name} in stock')

    return orders_repository.set_order_pending_and_reduce_stock(db, order)


def confirm_payment(order_id: int, db: Session):
    order = orders_repository.confirm_payment(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')
    return order


def user_cancel_payment(order_id: int, db: Session, user: models.User):
    order = orders_repository.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')

    if order.user_id != user.id:
        raise HTTPException(status_code=403, detail='You can only cancel your own order')

    if order.status != 'Pending':
        raise HTTPException(status_code=400, detail='Order is not pending')

    orders_repository.cancel_payment_and_restore(db, order)
    return {'message': 'Order canceled successfully'}


def admin_cancel_payment(order_id: int, db: Session):
    order = orders_repository.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')

    if order.status != 'Pending':
        raise HTTPException(status_code=400, detail='Order is not pending')

    orders_repository.cancel_payment_and_restore(db, order)
    return {'message': 'Order canceled successfully'}
