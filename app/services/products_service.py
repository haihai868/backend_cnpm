from typing import List, Optional, Tuple

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.repositories import products_repository


VALID_SIZES = ['S', 'M', 'L', 'XL', 'XXL']
VALID_AGE_GENDERS = ['Men', 'Women', 'Kids', 'Babies']


def get_product_by_id(db: Session, id: int) -> models.Product:
    product = products_repository.get_product_by_id(db, id)
    if not product:
        raise HTTPException(status_code=404, detail='Product not found')
    return product


def get_products_by_name(db: Session, name: str) -> List[models.Product]:
    products = products_repository.get_products_by_name(db, name)
    if not products:
        raise HTTPException(status_code=404, detail='Product not found')
    return products


def add_product(db: Session, product: schemas.ProductCreate) -> models.Product:
    category = db.query(models.Category).filter(models.Category.id == product.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail='Category not found')

    if product.age_gender and product.age_gender not in VALID_AGE_GENDERS:
        raise HTTPException(status_code=400, detail='Invalid age-gender')

    if product.size not in VALID_SIZES:
        raise HTTPException(status_code=400, detail='Invalid size')

    check_product = db.query(models.Product).filter(models.Product.name == product.name,
                                                    models.Product.size == product.size).first()

    if check_product:
        raise HTTPException(status_code=400, detail='Product with this size already exists')

    return products_repository.create_product(db, product.model_dump())


def update_product(db: Session, id: int, updated_product: schemas.ProductCreate) -> models.Product:
    product = products_repository.get_product_by_id(db, id)
    if not product:
        raise HTTPException(status_code=404, detail='Product not found')

    category = db.query(models.Category).filter(models.Category.id == updated_product.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail='Category not found')

    if updated_product.age_gender and updated_product.age_gender not in VALID_AGE_GENDERS:
        raise HTTPException(status_code=400, detail='Invalid age-gender')

    if updated_product.size not in VALID_SIZES:
        raise HTTPException(status_code=400, detail='Invalid size')

    updated = products_repository.update_product(db, id, updated_product.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail='Product not found')
    return updated


def get_products_by_criteria(db: Session,
                             skip: int = 0,
                             limit: Optional[int] = None,
                             search: Optional[str] = None,
                             category: Optional[str] = None,
                             sizes: Optional[List[str]] = None,
                             price_min: Optional[float] = None,
                             price_max: Optional[float] = None,
                             quantity_in_stock_min: Optional[int] = None,
                             quantity_in_stock_max: Optional[int] = None,
                             age_gender: Optional[str] = None,
                             max_rating: Optional[int] = None,
                             min_rating: Optional[int] = None,
                             is_on_sale: Optional[bool] = None
                             ) -> List[Tuple[models.Product, float]]:
    if sizes:
        for size in sizes:
            if size not in VALID_SIZES:
                raise HTTPException(status_code=400, detail='Invalid size')

    if age_gender and age_gender not in VALID_AGE_GENDERS:
        raise HTTPException(status_code=400, detail='Invalid age-gender')

    return products_repository.query_products_by_criteria(
        db, skip, limit, search, category, sizes, price_min, price_max,
        quantity_in_stock_min, quantity_in_stock_max, age_gender, max_rating,
        min_rating, is_on_sale
    )


def get_avg_rating(db: Session, id: int):
    result = products_repository.get_avg_rating(db, id)
    if not result:
        raise HTTPException(status_code=404, detail='Product not found')
    return {"product_id": id, "avg_rating": result.avg_rating}


def get_favourites_by_user_id(db: Session, user_id: int) -> List[models.Product]:
    favs = products_repository.get_favourites_by_user_id(db, user_id)
    if not favs:
        # keep behavior: return empty or 404? original raised 404 if user missing
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail='User not found')
    return favs


def add_favourite(db: Session, user: models.User, product_id: int) -> models.Product:
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail='Product not found')

    favourite = db.query(models.Favourite).filter(models.Favourite.user_id == user.id,
                                                  models.Favourite.product_id == product_id).first()
    if favourite:
        raise HTTPException(status_code=400, detail='Product already in favourites')

    return products_repository.add_favourite(db, user, product_id)


def delete_favourite(db: Session, user: models.User, product_id: int):
    ok = products_repository.delete_favourite(db, user, product_id)
    if not ok:
        raise HTTPException(status_code=404, detail='Favourite not found')
    return {'message': 'Favourite deleted successfully'}


def get_recommendations(db: Session, product_id: int) -> List[models.Product]:
    recs = products_repository.get_recommendations(db, product_id)
    if not recs:
        product = products_repository.get_product_by_id(db, product_id)
        if not product:
            raise HTTPException(status_code=404, detail='Product not found')
    return recs
