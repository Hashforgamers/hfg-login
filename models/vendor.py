from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Sequence
from sqlalchemy.orm import relationship
from app.extension import db  # Import db from the models package
from datetime import datetime

# Vendor model
class Vendor(db.Model):
    __tablename__ = 'vendors'
    
    id = Column(Integer, Sequence('vendor_id_seq', start=2000), primary_key=True)
    cafe_name = Column(String(255), nullable=False)
    owner_name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

