from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database_connect import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    fullname = Column(String(255), nullable=False)

    notifications = relationship('Notification', back_populates='user')
    orders = relationship('Order', back_populates='user')
    reviews = relationship('Review', back_populates='user')