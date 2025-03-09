from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database_connect import Base


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(255))

    products = relationship('Product', back_populates='category')