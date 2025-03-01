from sqlalchemy import Column, Integer, DateTime, func, ForeignKey, Enum, DECIMAL
from sqlalchemy.orm import relationship

from app.database_connect import Base

class Payment(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    payment_date = Column(DateTime, default=func.now())
    amount = Column(DECIMAL(10, 2), nullable=False)
    payment_method = Column(Enum('Cash', 'CreditCard', 'BankTransfer', 'E-Wallet', name="payment_method_enum"))
    ship_fee = Column(DECIMAL(10, 2), nullable=False)
    status = Column(Enum('Pending', 'Completed', 'Failed', name="payment_status_enum"), default='Pending')

    order = relationship("Order", back_populates="payments")
