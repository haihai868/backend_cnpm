from datetime import datetime
from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.repositories import sales_repository


VALID_AGE_GENDERS = ['Men', 'Women', 'Kids', 'Babies']


def get_all_sales(db: Session) -> List[models.Sale]:
    return sales_repository.get_all_sales(db)


def get_sale_by_id(id: int, db: Session):
    sale = sales_repository.get_sale_by_id(db, id)
    if not sale:
        raise HTTPException(status_code=404, detail='Sale not found')
    return sale


def create_sale(sale: schemas.SaleCreate, db: Session, admin: models.Admin):
    products_query = sales_repository.get_products_for_sale(db, sale)

    if sale.age_gender and sale.age_gender not in VALID_AGE_GENDERS:
        raise HTTPException(status_code=400, detail='Invalid age-gender')

    if sale.discount_percentage < 0 or sale.discount_percentage >= 100:
        raise HTTPException(status_code=400, detail='Invalid discount percentage')

    sales_repository.apply_sale_to_products(db, products_query, sale.discount_percentage)
    return sales_repository.create_sale(db, sale.model_dump())


def end_sale(id: int, db: Session, admin: models.Admin):
    sale = sales_repository.get_sale_by_id(db, id)
    if not sale:
        raise HTTPException(status_code=404, detail='Sale not found')

    products = sales_repository.get_products_for_sale(db, sale)
    sales_repository.end_sale_on_products(db, products, sale)
    return sales_repository.end_sale(db, id)
