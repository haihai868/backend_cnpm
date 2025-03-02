from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.database_connect import Base

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(Enum('Paid', 'Unpaid'), nullable=False)
    description = Column(String(255))
    created_at = Column(DateTime, default=func.now())

    user = relationship('User', back_populates='orders')
    order_details = relationship('OrderDetail', back_populates='order')
    payments = relationship('Payment', back_populates='order')