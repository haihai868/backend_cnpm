from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas, security
from app.database_connect import get_db

router = APIRouter(
    prefix='/sales',
    tags=['sales']
)

@router.get('/{id}', response_model=schemas.SaleOut)
def get_sale_by_id(id: int, db: Session = Depends(get_db)):
    sale = db.query(models.Sale).filter(models.Sale.id == id).first()
    if not sale:
        raise HTTPException(status_code=404, detail='Sale not found')

    return sale

@router.post('/', status_code=201, response_model=schemas.SaleOut)
def create_sale(sale: schemas.SaleCreate, db: Session = Depends(get_db), admin: models.Admin = Depends(security.get_current_admin)):
    products_query = db.query(models.Product)
    if sale.category_id:
        category = db.query(models.Category).filter(models.Category.id == sale.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail='Category not found')
        products_query = products_query.join(models.Category).filter(models.Category.id == sale.category_id)

    if sale.age_gender:
        if sale.age_gender not in ['Men', 'Women', 'Kids', 'Babies']:
            raise HTTPException(status_code=400, detail='Invalid age-gender')

        products_query = products_query.filter(models.Product.age_gender == sale.age_gender)
    products = products_query.all()

    if sale.discount_percentage < 0 or sale.discount_percentage >= 100:
        raise HTTPException(status_code=400, detail='Invalid discount percentage')

    for product in products:
        if not product.old_price:
            product.old_price = product.price
            product.price = product.price * (1 - sale.discount_percentage / 100)
        else:
            product.price -= product.old_price * sale.discount_percentage / 100
        db.commit()
        db.refresh(product)

    new_sale = models.Sale(**sale.model_dump())
    db.add(new_sale)
    db.commit()
    db.refresh(new_sale)
    return new_sale

@router.put('/{id}', response_model=schemas.SaleOut)
def end_sale(id: int, db: Session = Depends(get_db), admin: models.Admin = Depends(security.get_current_admin)):
    sale_query = db.query(models.Sale).filter(models.Sale.id == id)
    sale = sale_query.first()
    if not sale:
        raise HTTPException(status_code=404, detail='Sale not found')

    products_query = db.query(models.Product)
    if sale.category_id:
        products_query = products_query.join(models.Category).filter(models.Category.id == sale.category_id)
    if sale.age_gender:
        products_query = products_query.filter(models.Product.age_gender == sale.age_gender)
    products = products_query.all()

    for product in products:
        product.price += product.old_price * (sale.discount_percentage / 100)
        if product.price == product.old_price:
            product.old_price = None
        db.commit()
        db.refresh(product)

    sale.end_date = datetime.now()

    db.commit()
    db.refresh(sale)
    return sale
