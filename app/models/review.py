from sqlalchemy import Column, Integer, DateTime, func, ForeignKey, Enum, String
from sqlalchemy.orm import relationship

from app.database_connect import Base


class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    rating = Column(Enum('1', '2', '3', '4', '5', name='rating_enum'), nullable=False)
    comment = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())

    user = relationship('User', back_populates='reviews')
    product = relationship('Product', back_populates='reviews')