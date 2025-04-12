from sqlalchemy import Column, Integer, DateTime, func, ForeignKey, Enum, DECIMAL, String
from sqlalchemy.orm import relationship

from app.database_connect import Base

class Payment(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), unique=True, nullable=False)
    payment_date = Column(DateTime, server_default=func.now())
    shipping_fee = Column(DECIMAL(10, 2), nullable=False)
    address = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    payment_method = Column(Enum('Cash', 'Credit Card', 'PayPal', name='payment_method_enum'), nullable=False)
    status = Column(Enum('Pending', 'Completed', 'Failed', name='payment_status_enum'), nullable=False)

    order = relationship("Order", back_populates="payment")
