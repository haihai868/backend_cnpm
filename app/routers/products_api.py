import random
from typing import List, Optional, Tuple

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from app import models, schemas, security
from app.database_connect import get_db
from chatbot.rag_src import astradb_retrievers
from chatbot.rag_src.utils import create_product_document

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

@router.get("/name/{name}")
def get_products_by_name(name: str, db: Session = Depends(get_db)):
    products = db.query(models.Product).filter(models.Product.name == name).all()

    if not products:
        raise HTTPException(status_code=404, detail='Product not found')

    return products

@router.post('/', status_code=201, response_model=schemas.ProductOut)
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

    doc = create_product_document(new_product.__dict__)
    astradb_retrievers.prods_vstore.add_documents(documents=[doc], ids=[str(new_product.id)])

    return new_product

@router.put('/{id}', response_model=schemas.ProductOut)
def update_product(updated_product: schemas.ProductCreate, id: int, db: Session = Depends(get_db)):
    product_query = db.query(models.Product).filter(models.Product.id == id)

    product = product_query.first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    category = db.query(models.Category).filter(models.Category.id == updated_product.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail='Category not found')

    if updated_product.age_gender and updated_product.age_gender not in ['Men', 'Women', 'Kids', 'Babies']:
        raise HTTPException(status_code=400, detail='Invalid age-gender')

    if updated_product.size not in ['S', 'M', 'L', 'XL', 'XXL']:
        raise HTTPException(status_code=400, detail='Invalid size')

    product_query.update(updated_product.model_dump(), synchronize_session=False)

    db.commit()
    db.refresh(product)

    doc = create_product_document(product.__dict__)
    astradb_retrievers.prods_vstore.delete(ids=[str(id)])
    astradb_retrievers.prods_vstore.add_documents(documents=[doc], ids=[str(id)])

    return product

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
    query = (db.query(models.Product,
                     func.coalesce(func.avg(models.Review.rating), 0).label('avg_rating')
                     )
             .outerjoin(models.Review, models.Review.product_id == models.Product.id)
             .group_by(models.Product.id))

    if is_on_sale is not None:
        if is_on_sale:
            query = query.filter(models.Product.old_price != None)
        else:
            query = query.filter(models.Product.old_price == None)

    if max_rating is not None:
        query = query.having(func.coalesce(func.avg(models.Review.rating), 0) <= max_rating)
    if min_rating is not None:
        query = query.having(func.coalesce(func.avg(models.Review.rating), 0) >= min_rating)

    if search:
        query = query.filter(
            or_(
                models.Product.name.like(f'%{search}%'),
                models.Product.description.like(f'%{search}%')
            )
        )

    if category:
        query = query.join(models.Category).filter(models.Category.name == category)

    if sizes:
        for size in sizes:
            if size not in ['S', 'M', 'L', 'XL', 'XXL']:
                raise HTTPException(status_code=400, detail='Invalid size')
        query = query.filter(models.Product.size.in_(sizes))

    if price_min is not None:
        query = query.filter(models.Product.price >= price_min)
    if price_max is not None:
        query = query.filter(models.Product.price <= price_max)

    if quantity_in_stock_min is not None:
        query = query.filter(models.Product.quantity_in_stock >= quantity_in_stock_min)
    if quantity_in_stock_max is not None:
        query = query.filter(models.Product.quantity_in_stock <= quantity_in_stock_max)

    if age_gender:
        if age_gender not in ['Men', 'Women', 'Kids', 'Babies']:
            raise HTTPException(status_code=400, detail='Invalid age-gender')
        query = query.filter(models.Product.age_gender == age_gender)

    query = query.offset(skip).limit(limit)
    products = query.all()

    return products

@router.get("/avg_rating/{id}")
def get_avg_rating(id: int, db: Session = Depends(get_db)):
    result = (
        db.query(
            models.Product.id,
            func.coalesce(func.avg(models.Review.rating), 0).label("avg_rating")
        )
        .outerjoin(models.Review, models.Review.product_id == models.Product.id)
        .filter(models.Product.id == id)
        .group_by(models.Product.id)
        .first()
    )

    if not result:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"product_id": id, "avg_rating": result.avg_rating}

@router.get("/user/favourites/{user_id}", response_model=List[schemas.ProductOut])
def get_favourites_by_user_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    fav_products = [favourite.product for favourite in user.favourites]
    return fav_products

@router.post("/user/favourite/{product_id}", status_code=201, response_model=schemas.ProductOut)
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

@router.delete("/favourite/{product_id}")
def delete_favourite(product_id: int, db: Session = Depends(get_db), user: models.User = Depends(security.get_current_user)):
    favourite = db.query(models.Favourite).filter(models.Favourite.product_id == product_id,
                                                  models.Favourite.user_id == user.id).first()
    if not favourite:
        raise HTTPException(status_code=404, detail='Favourite not found')

    db.delete(favourite)
    db.commit()
    return {'message': 'Favourite deleted successfully'}


@router.get("/recommendations/{product_id}", response_model=List[schemas.ProductOut])
def get_product_recommendations(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail='Product not found')

    products = db.query(models.Product).filter(models.Product.category_id == product.category_id,
                                               models.Product.name != product.name).all()

    unique_products_dict = {}
    for p in products:
        if p.name not in unique_products_dict:
            unique_products_dict[p.name] = p

    unique_products = list(unique_products_dict.values())

    recommended_products = random.sample(unique_products, min(len(products), 4))
    return recommended_products