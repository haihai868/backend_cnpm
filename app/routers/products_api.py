import random
from typing import List, Optional, Tuple

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from app import models, schemas, security
from app.services import products_service
from app.database_connect import get_db

router = APIRouter(
    prefix='/products',
    tags=['products']
)

@router.get("/{id}")
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    return products_service.get_product_by_id(db, id)

@router.get("/name/{name}")
def get_products_by_name(name: str, db: Session = Depends(get_db)):
    return products_service.get_products_by_name(db, name)

@router.post('/', status_code=201, response_model=schemas.ProductOut)
def add_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    return products_service.add_product(db, product)

@router.put('/{id}', response_model=schemas.ProductOut)
def update_product(updated_product: schemas.ProductCreate, id: int, db: Session = Depends(get_db)):
    return products_service.update_product(db, id, updated_product)

@router.get('/', response_model=List[Tuple[schemas.ProductOut, float]])
def get_products_by_criteria(db: Session = Depends(get_db),
                             skip: int = 0,
                             limit: int = Query(None, le=100),
                             search: Optional[str] = None,
                             category: Optional[str] = None,
                             sizes: List[Optional[str]] = Query(None, alias='size'),
                             price_min: Optional[float] = Query(None, alias='priceMin'),
                             price_max: Optional[float] = Query(None, alias='priceMax'),
                             quantity_in_stock_min: Optional[int] = Query(None, alias='quantityInStockMin'),
                             quantity_in_stock_max: Optional[int] = Query(None, alias='quantityInStockM_ax'),
                             age_gender: Optional[str] = Query(None, alias='ageGender'),
                             max_rating: Optional[int] = Query(None, alias='maxRating'),
                             min_rating: Optional[int] = Query(None, alias='minRating'),
                             is_on_sale: Optional[bool] = Query(None, alias='isOnSale')
                             ):
    return products_service.get_products_by_criteria(
        db, skip, limit, search, category, sizes, price_min, price_max,
        quantity_in_stock_min, quantity_in_stock_max, age_gender, max_rating,
        min_rating, is_on_sale
    )

@router.get("/avg_rating/{id}")
def get_avg_rating(id: int, db: Session = Depends(get_db)):
    return products_service.get_avg_rating(db, id)

@router.get("/user/favourites/{user_id}", response_model=List[schemas.ProductOut])
def get_favourites_by_user_id(user_id: int, db: Session = Depends(get_db)):
    return products_service.get_favourites_by_user_id(db, user_id)

@router.post("/user/favourite/{product_id}", status_code=201, response_model=schemas.ProductOut)
def add_favourite(product_id: int, db: Session = Depends(get_db), user: models.User = Depends(security.get_current_user)):
    return products_service.add_favourite(db, user, product_id)

@router.delete("/favourite/{product_id}")
def delete_favourite(product_id: int, db: Session = Depends(get_db), user: models.User = Depends(security.get_current_user)):
    return products_service.delete_favourite(db, user, product_id)


@router.get("/recommendations/{product_id}", response_model=List[schemas.ProductOut])
def get_product_recommendations(product_id: int, db: Session = Depends(get_db)):
    return products_service.get_recommendations(db, product_id)