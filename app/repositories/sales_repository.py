from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from app import models


def get_all_sales(db: Session) -> List[models.Sale]:
    return db.query(models.Sale).all()


def get_sale_by_id(db: Session, id: int) -> Optional[models.Sale]:
    return db.query(models.Sale).filter(models.Sale.id == id).first()


def get_products_for_sale(db: Session, sale):
    products_query = db.query(models.Product)
    if sale.category_id:
        products_query = products_query.join(models.Category).filter(models.Category.id == sale.category_id)
    if sale.age_gender:
        products_query = products_query.filter(models.Product.age_gender == sale.age_gender)
    return products_query.all()


def apply_sale_to_products(db: Session, products, discount_percentage: float):
    for product in products:
        if not product.old_price:
            product.old_price = product.price
            product.price = product.price * (1 - discount_percentage / 100)
        else:
            product.price -= product.old_price * discount_percentage / 100
        db.commit()
        db.refresh(product)


def end_sale_on_products(db: Session, products, sale):
    for product in products:
        product.price += product.old_price * (sale.discount_percentage / 100)
        if product.price == product.old_price:
            product.old_price = None
        db.commit()
        db.refresh(product)


def create_sale(db: Session, sale_data: dict) -> models.Sale:
    new_sale = models.Sale(**sale_data)
    db.add(new_sale)
    db.commit()
    db.refresh(new_sale)
    return new_sale


def end_sale(db: Session, sale_id: int):
    sale = get_sale_by_id(db, sale_id)
    if not sale:
        return None
    sale.end_date = datetime.now()
    db.commit()
    db.refresh(sale)
    return sale
