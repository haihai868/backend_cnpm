from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from app import models


def get_all_orders(db: Session) -> List[models.Order]:
    return db.query(models.Order).all()


def get_sale_quantity(db: Session):
    return db.query(models.OrderDetail).join(models.Order).filter(models.Order.status == 'Paid').all()


def get_unpaid_order_by_user(db: Session, user_id: int) -> Optional[models.Order]:
    return db.query(models.Order).filter(models.Order.user_id == user_id, models.Order.status == 'Unpaid').first()


def get_order_by_id(db: Session, order_id: int) -> Optional[models.Order]:
    return db.query(models.Order).filter(models.Order.id == order_id).first()


def create_order(db: Session, order_data: dict) -> models.Order:
    new_order = models.Order(**order_data)
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order


def update_order(db: Session, user_id: int, order_data: dict):
    q = db.query(models.Order).filter(models.Order.user_id == user_id, models.Order.status == 'Unpaid')
    if not q.first():
        return None
    q.update(order_data, synchronize_session=False)
    db.commit()
    return q.first()


def add_order_detail(db: Session, order_id: int, product_id: int, quantity: int, priceEach: float, price_override=None):
    order_detail = db.query(models.OrderDetail).filter(models.OrderDetail.product_id == product_id,
                                                      models.OrderDetail.order_id == order_id).first()
    if order_detail:
        return None

    od = models.OrderDetail(product_id=product_id, order_id=order_id, quantity=quantity, priceEach=priceEach if price_override is None else price_override)
    db.add(od)
    db.commit()
    db.refresh(od)
    return od


def delete_order_detail(db: Session, product_id: int, order_id: int):
    od = db.query(models.OrderDetail).filter(models.OrderDetail.product_id == product_id,
                                             models.OrderDetail.order_id == order_id).first()
    if not od:
        return False
    db.delete(od)
    db.commit()
    return True


def get_orders_by_user_and_status(db: Session, user_id: int, status: str):
    if status == 'All':
        return db.query(models.Order).filter(models.Order.user_id == user_id).all()
    return db.query(models.Order).filter(models.Order.user_id == user_id, models.Order.status == status).all()


def calculate_total(db: Session, order_id: int):
    order = get_order_by_id(db, order_id)
    if not order:
        return None
    total = 0
    for od in order.order_details:
        total += od.product.price * od.quantity
    return total


def set_order_pending_and_reduce_stock(db: Session, order: models.Order):
    order.status = 'Pending'
    order.started_payment_at = datetime.now()
    for od in order.order_details:
        od.product.quantity_in_stock -= od.quantity
    db.commit()
    db.refresh(order)
    return order


def confirm_payment(db: Session, order_id: int):
    order = get_order_by_id(db, order_id)
    if not order:
        return None
    order.status = 'Paid'
    order.confirmed_at = datetime.now()
    db.commit()
    db.refresh(order)
    return order


def cancel_payment_and_restore(db: Session, order: models.Order):
    for od in order.order_details:
        od.product.quantity_in_stock += od.quantity
        db.delete(od)
    db.delete(order)
    db.commit()
