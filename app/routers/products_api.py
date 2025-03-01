from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.database_connect import get_db

router = APIRouter(
    prefix='/products',
    tags=['products']
)

@router.get("/{id}")
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == id).first()

    if not product:
        raise HTTPException(status_code=404, detail='Product not found')
    
    return product

@router.post('/', response_model=schemas.ProductOut)
def add_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.id == product.category_id).first()

    if not category:
        raise HTTPException(status_code=404, detail='Category not found')

    if product.size not in ['S', 'M', 'L', 'XL']:
        raise HTTPException(status_code=400, detail='Invalid size')

    new_product = models.Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.get('/', response_model=List[schemas.ProductOut])
def get_products_by_criteria(db: Session = Depends(get_db),
                             search: Optional[str] = None,
                             category: Optional[str] = None,
                             size: Optional[str] = None,
                             price_min: Optional[float] = Query(None, alias='priceMin'),
                             price_max: Optional[float] = Query(None, alias='priceMax'),
                             quantity_in_stock_min: Optional[int] = Query(None, alias='quantityInStockMin'),
                             quantity_in_stock_max: Optional[int] = Query(None, alias='quantityInStockMax')
                             ):
    query = db.query(models.Product)

    if search:
        query = query.filter(
            models.Product.name.like(f'%{search}%')
            | models.Product.description.like(f'%{search}%')
        )

    if category:
        query = query.join(models.Category).filter(models.Category.name == category)

    if size:
        query = query.filter(models.Product.size == size)

    if price_min is not None:
        query = query.filter(models.Product.price >= price_min)

    if price_max is not None:
        query = query.filter(models.Product.price <= price_max)

    if quantity_in_stock_min is not None:
        query = query.filter(models.Product.quantity_in_stock >= quantity_in_stock_min)

    if quantity_in_stock_max is not None:
        query = query.filter(models.Product.quantity_in_stock <= quantity_in_stock_max)

    return query.all()

