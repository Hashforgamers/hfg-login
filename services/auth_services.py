from werkzeug.security import check_password_hash
from models.user import User
from models.vendor import Vendor
from models.contactInfo import ContactInfo
from models.passwordManager import PasswordManager
from utils.jwt_helper import create_jwt_token
from app.extension import db
from sqlalchemy import and_
from flask import current_app
from utils.token_blacklist import add_to_blacklist

def login(email, password, parent_type):
    """Authenticate a user or vendor and return a JWT token."""
    current_app.logger.info(f"Login Started")
    if parent_type not in ['user', 'vendor']:
        return None, "Invalid parent_type"

    current_app.logger.info(f"Test 1 : {email}")
    # Fetch ContactInfo for the given email
    contact_info = ContactInfo.query.filter_by(email=email).first()
    if not contact_info:
        return None, "Invalid credentials"

    # Validate parent_type and parent_id
    if contact_info.parent_type != parent_type:
        return None, "Invalid credentials"

    current_app.logger.info(f"Test 2")
    # Fetch PasswordManager entry
    password_manager = PasswordManager.query.filter_by(
        parent_id=contact_info.parent_id,
        parent_type=contact_info.parent_type
    ).first()

    current_app.logger.info(f"Test 3")
    if not password_manager:
        return None, "Invalid credentials"

    current_app.logger.info(f"Test 4 {password_manager.password} {password}")
    # Verify password
    if password_manager.password != password:
        return None, "Invalid credentials"

    current_app.logger.info(f"Test 5")
    # Fetch account (User or Vendor)
    if parent_type == 'user':
        account = User.query.filter_by(id=contact_info.parent_id).first()
    else:  # parent_type == 'vendor'
        account = Vendor.query.filter_by(id=contact_info.parent_id).first()

    current_app.logger.info(f"Test 6")
    if not account:
        return None, "Invalid credentials"

    # Generate JWT token
    token = create_jwt_token(identity={'id': account.id, 'type': parent_type})
    return token, None


def invalidate_token(token):
    """
    Invalidate a JWT token by adding it to the blacklist.

    :param token: The JWT token to invalidate.
    :return: Tuple of (success: bool, message: str).
    """
    try:
        current_app.logger.info("Invalidating token")

        # Add token to the blacklist
        success = add_to_blacklist(token)
        if not success:
            current_app.logger.warning("Failed to add token to the blacklist")
            return False, "Failed to invalidate token"

        current_app.logger.info("Token invalidated successfully")
        return True, "Token invalidated successfully"

    except Exception as e:
        current_app.logger.error(f"Error invalidating token: {str(e)}")
        return False, "An error occurred while invalidating the token"
