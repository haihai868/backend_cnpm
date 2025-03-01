from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship

from app.database_connect import Base


class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(String(255), nullable=False)
    is_read = Column(Boolean, server_default='false')
    created_at = Column(DateTime, server_default=func.now())

    user = relationship('User', back_populates='notifications')