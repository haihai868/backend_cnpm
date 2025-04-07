from sqlalchemy import Column, Integer, String

from app.database_connect import Base


class Admin(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True)
    password = Column(String(100), unique=True)
    email = Column(String(100), unique=True)
