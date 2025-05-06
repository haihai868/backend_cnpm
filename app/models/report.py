from sqlalchemy import Integer, Column, ForeignKey, String, DateTime, func
from sqlalchemy.orm import relationship

from app.database_connect import Base


class Report(Base):
    __tablename__ = 'reports'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    message = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship('User', back_populates='reports')