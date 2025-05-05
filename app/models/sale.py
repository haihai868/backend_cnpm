from sqlalchemy import Column, Integer, Enum, ForeignKey, Float, func, DateTime
from sqlalchemy.orm import relationship

from app.database_connect import Base

class Sale(Base):
    __tablename__ = 'sales'

    id = Column(Integer, primary_key=True)
    age_gender = Column(Enum('Men', 'Women', 'Kids', 'Babies', name='age_gender_enum'), nullable=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    discount_percentage = Column(Float, nullable=False)
    start_date = Column(DateTime, server_default=func.now())
    end_date = Column(DateTime, nullable=True)

    category = relationship('Category', back_populates='sales')