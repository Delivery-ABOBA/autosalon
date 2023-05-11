from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean

from app.database.database import DataBase


class Users(DataBase):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    login = Column(String(90), nullable=False, unique=True)
    password = Column(String(300), nullable=False)
