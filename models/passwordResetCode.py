# models/passwordResetCode.py

import random
import string
from datetime import datetime, timedelta
from app.extension import db


class PasswordResetCode(db.Model):
    __tablename__ = 'password_reset_codes'

    id           = db.Column(db.Integer, primary_key=True)
    account_id   = db.Column(db.Integer, db.ForeignKey('vendor_accounts.id'), nullable=False)
    code         = db.Column(db.String(6), nullable=False)
    is_used      = db.Column(db.Boolean, default=False)
    expires_at   = db.Column(db.DateTime, nullable=False)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    account = db.relationship('VendorAccount', backref='reset_codes')

    @staticmethod
    def generate_code():
        return ''.join(random.choices(string.digits, k=6))

    def is_valid(self):
        return not self.is_used and datetime.utcnow() < self.expires_at
