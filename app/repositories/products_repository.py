import random
from typing import List, Optional, Tuple

from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from app import models


def get_product_by_id(db: Session, id: int) -> Optional[models.Product]:
    return db.query(models.Product).filter(models.Product.id == id).first()


def get_products_by_name(db: Session, name: str) -> List[models.Product]:
    return db.query(models.Product).filter(models.Product.name == name).all()


def create_product(db: Session, product_data: dict) -> models.Product:
    new_product = models.Product(**product_data)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


def update_product(db: Session, id: int, product_data: dict) -> Optional[models.Product]:
    product_query = db.query(models.Product).filter(models.Product.id == id)
    product = product_query.first()
    if not product:
        return None
    product_query.update(product_data, synchronize_session=False)
    db.commit()
    db.refresh(product)
    return product


def query_products_by_criteria(db: Session,
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
        query = query.filter(models.Product.age_gender == age_gender)

    query = query.offset(skip).limit(limit)
    return query.all()


def get_avg_rating(db: Session, id: int):
    return (
        db.query(
            models.Product.id,
            func.coalesce(func.avg(models.Review.rating), 0).label("avg_rating")
        )
        .outerjoin(models.Review, models.Review.product_id == models.Product.id)
        .filter(models.Product.id == id)
        .group_by(models.Product.id)
        .first()
    )


def get_favourites_by_user_id(db: Session, user_id: int) -> List[models.Product]:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return []
    return [favourite.product for favourite in user.favourites]


def add_favourite(db: Session, user: models.User, product_id: int) -> Optional[models.Product]:
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        return None

    favourite = db.query(models.Favourite).filter(models.Favourite.user_id == user.id,
                                                  models.Favourite.product_id == product_id).first()

    if favourite:
        return None

    user.favourites.append(models.Favourite(product_id=product_id))
    db.commit()
    return product


def delete_favourite(db: Session, user: models.User, product_id: int) -> bool:
    favourite = db.query(models.Favourite).filter(models.Favourite.product_id == product_id,
                                                  models.Favourite.user_id == user.id).first()
    if not favourite:
        return False

    db.delete(favourite)
    db.commit()
    return True


def get_recommendations(db: Session, product_id: int, limit: int = 4) -> List[models.Product]:
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        return []

    products = db.query(models.Product).filter(models.Product.category_id == product.category_id,
                                               models.Product.name != product.name).all()

    unique_products_dict = {}
    for p in products:
        if p.name not in unique_products_dict:
            unique_products_dict[p.name] = p

    unique_products = list(unique_products_dict.values())
    if not unique_products:
        return []

    recommended_products = random.sample(unique_products, min(len(unique_products), limit))
    return recommended_products
