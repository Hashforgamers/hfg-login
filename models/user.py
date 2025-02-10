from sqlalchemy import Column, Integer, String, Sequence
from sqlalchemy.orm import relationship
from .passwordManager import PasswordManager
from app.extension import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = Column(Integer, Sequence('user_id_seq', start=2000), primary_key=True)
    fid = Column(String(255), unique=True, nullable=False)
    
    parent_type = Column(String(50), nullable=False, default='user')
