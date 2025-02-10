from sqlalchemy.orm import relationship, foreign
from sqlalchemy import Column, Integer, String,ForeignKey
from app.extension import db
from sqlalchemy.ext.declarative import declared_attr

class PasswordManager(db.Model):
    __tablename__ = 'password_manager'

    id = Column(Integer, primary_key=True)
    userid = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)

    parent_id = Column(Integer, nullable=False)
    parent_type = Column(String(50), nullable=False)
