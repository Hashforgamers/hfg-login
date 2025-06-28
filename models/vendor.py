from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Sequence
from sqlalchemy.orm import relationship
from app.extension import db  # Import db from the models package
from datetime import datetime
from models.vendorAccount import VendorAccount
from models.vendorPin import VendorPin

# Vendor model
class Vendor(db.Model):
    __tablename__ = 'vendors'
    
    id = Column(Integer, Sequence('vendor_id_seq', start=2000), primary_key=True)
    cafe_name = Column(String(255), nullable=False)
    owner_name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    account_id = Column(Integer, ForeignKey('vendor_accounts.id'), nullable=True)
    account = relationship('VendorAccount', back_populates='vendors')

    pin = relationship('VendorPin', back_populates='vendor', uselist=False, cascade="all, delete-orphan")
