from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.extension import db


class Console(db.Model):
    __tablename__ = 'consoles'

    id = Column(Integer, primary_key=True)
    vendor_id = Column(Integer, ForeignKey('vendors.id', ondelete='CASCADE'), nullable=False, index=True)
    console_number = Column(Integer, nullable=False, index=True)
    model_number = Column(String(50), nullable=False)
    serial_number = Column(String(100), nullable=False)
    brand = Column(String(50), nullable=False)
    console_type = Column(String(50), nullable=False)
    release_date = Column(Date, nullable=True)
    description = Column(String(500), nullable=True)

    vendor = relationship('Vendor', back_populates='consoles')

    def __repr__(self):
        return f"<Console vendor_id={self.vendor_id} number={self.console_number} type={self.console_type}>"
