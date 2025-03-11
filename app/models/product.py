from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.database_connect import Base


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255))
    old_price = Column(Float)
    price = Column(Float, nullable=False)
    quantity_in_stock = Column(Integer, nullable=False, server_default='0')
    size = Column(Enum('S', 'M', 'L', 'XL', 'XXL', name='size_enum'))
    age_gender = Column(Enum('Men', 'Women', 'Kids', 'Babies', name='age_gender_enum'))
    category_id = Column(Integer, ForeignKey('categories.id'))
    image = Column(String(255))

    category = relationship('Category', back_populates='products')
    order_details = relationship('OrderDetail', back_populates='product')
    reviews = relationship('Review', back_populates='product')
    favourites = relationship('Favourite', back_populates='product')