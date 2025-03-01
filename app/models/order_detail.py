from sqlalchemy import Column, Integer, ForeignKey, String, Float, Numeric
from sqlalchemy.orm import relationship

from app.database_connect import Base


class OrderDetail(Base):
    __tablename__ = 'order_details'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    priceEach = Column(Numeric(10, 2), nullable=False)

    order = relationship('Order', back_populates='order_details')
    product = relationship('Product', back_populates='order_details')