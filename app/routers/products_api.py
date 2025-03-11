from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import models, schemas, security
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

@router.get("/byName/{name}")
def get_products_by_name(name: str, db: Session = Depends(get_db)):
    products = db.query(models.Product).filter(models.Product.name == name).all()

    if not products:
        raise HTTPException(status_code=404, detail='Product not found')

    return products

@router.post('/', response_model=schemas.ProductOut)
def add_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.id == product.category_id).first()

    if not category:
        raise HTTPException(status_code=404, detail='Category not found')

    if product.age_gender and product.age_gender not in ['Men', 'Women', 'Kids', 'Babies']:
        raise HTTPException(status_code=400, detail='Invalid age-gender')

    if product.size not in ['S', 'M', 'L', 'XL', 'XXL']:
        raise HTTPException(status_code=400, detail='Invalid size')

    check_product = db.query(models.Product).filter(models.Product.name == product.name,
                                                    models.Product.size == product.size).first()

    if check_product:
        raise HTTPException(status_code=400, detail='Product with this size already exists')

    new_product = models.Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.put('/{id}', response_model=schemas.ProductOut)
def update_product(updated_product: schemas.ProductCreate, id: int, db: Session = Depends(get_db)):
    product_query = db.query(models.Product).filter(models.Product.id == id)

    product = product_query.first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product_query.update(updated_product.model_dump(), synchronize_session=False)

    db.commit()
    return product_query.first()

@router.get('/', response_model=List[schemas.ProductOut])
def get_products_by_criteria(db: Session = Depends(get_db),
                             search: Optional[str] = None,
                             category: Optional[str] = None,
                             size: Optional[str] = None,
                             price_min: Optional[float] = Query(None, alias='priceMin'),
                             price_max: Optional[float] = Query(None, alias='priceMax'),
                             quantity_in_stock_min: Optional[int] = Query(None, alias='quantityInStockMin'),
                             quantity_in_stock_max: Optional[int] = Query(None, alias='quantityInStockMax'),
                             age_gender: Optional[str] = Query(None, alias='ageGender')
                             ):
    query = db.query(models.Product)

    if search:
        query = query.filter(
            or_(
                models.Product.name.like(f'%{search}%'),
                models.Product.description.like(f'%{search}%')
            )
        )

    if category:
        query = query.join(models.Category).filter(models.Category.name == category)

    if size and size in ['S', 'M', 'L', 'XL', 'XXL']:
        query = query.filter(models.Product.size == size)

    if price_min is not None:
        query = query.filter(models.Product.price >= price_min)

    if price_max is not None:
        query = query.filter(models.Product.price <= price_max)

    if quantity_in_stock_min is not None:
        query = query.filter(models.Product.quantity_in_stock >= quantity_in_stock_min)

    if quantity_in_stock_max is not None:
        query = query.filter(models.Product.quantity_in_stock <= quantity_in_stock_max)

    if age_gender and age_gender in ['Men', 'Women', 'Kids', 'Babies']:
        query = query.filter(models.Product.age_gender == age_gender)

    return query.all()

@router.get("/avg_rating/{id}")
def get_avg_rating(id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if len(product.reviews) == 0:
        return {"product_id": id, "avg_rating": 0}

    avg_rating = 0
    for review in product.reviews:
        avg_rating += int(review.rating)

    avg_rating /= len(product.reviews)
    return {"product_id": id, "avg_rating": avg_rating}

@router.get("/user/favourites/{user_id}", response_model=List[schemas.ProductOut])
def get_favourites_by_user_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    fav_products = [favourite.product for favourite in user.favourites]
    return fav_products

@router.post("/user/add-favourite/{product_id}", response_model=schemas.ProductCreate)
def add_favourite(product_id: int, db: Session = Depends(get_db), user: models.User = Depends(security.get_current_user)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail='Product not found')

    favourite = db.query(models.Favourite).filter(models.Favourite.user_id == user.id,
                                                  models.Favourite.product_id == product_id).first()

    if favourite:
        raise HTTPException(status_code=400, detail='Product already in favourites')

    user.favourites.append(models.Favourite(product_id=product_id))
    db.commit()
    return product