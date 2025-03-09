from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database_connect import Base


class Favourite(Base):
    __tablename__ = 'favourites'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))

    user = relationship('User', back_populates='favourites')
    product = relationship('Product', back_populates='favourites')
    __table_args__ = (UniqueConstraint('user_id', 'product_id', name='unique_favourite'))