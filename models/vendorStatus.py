from datetime import datetime  # Add this line
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.extension import db

class VendorStatus(db.Model):
    __tablename__ = 'vendor_statuses'
    
    id = Column(Integer, primary_key=True)
    vendor_id = Column(Integer, ForeignKey('vendors.id'), nullable=False)
    status = Column(String, nullable=False)  # e.g., 'active', 'inactive', 'pending_verification'
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Link to Vendor model
    vendor = relationship("Vendor", back_populates="statuses")
