import jwt
from datetime import datetime, timedelta
from flask import current_app
from werkzeug.exceptions import Unauthorized
import os

# In-memory blacklist for demonstration purposes (use Redis or database in production)
BLACKLISTED_TOKENS = set()

# Get the secret key from the Flask app config
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev")

# Default expiration time for tokens (in minutes)
DEFAULT_EXPIRATION_MINUTES = 60

def create_jwt_token(identity):
    """Generate a JWT token."""
    payload = {
        'sub': identity,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=48)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def decode_token(token):
    """
    Decode a JWT token.

    :param token: Encoded JWT token as a string.
    :return: Decoded payload as a dictionary.
    :raises: Unauthorized if the token is invalid or expired.
    """
    try:
        decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return decoded_payload
    except jwt.ExpiredSignatureError:
        raise Unauthorized("Token has expired.")
    except jwt.InvalidTokenError:
        raise Unauthorized("Invalid token.")


def validate_token(token):
    """
    Validate the given token by decoding it and checking if it's blacklisted.

    :param token: JWT token as a string.
    :return: Decoded token if valid.
    :raises: Unauthorized if invalid, expired, or blacklisted.
    """
    if is_token_blacklisted(token):
        raise Unauthorized("Token has been revoked.")
    return decode_token(token)


def is_token_blacklisted(token):
    """
    Check if the token is blacklisted.

    :param token: JWT token as a string.
    :return: Boolean indicating if the token is blacklisted.
    """
    return token in BLACKLISTED_TOKENS


def revoke_token(token):
    """
    Revoke a token by adding it to a blacklist.

    :param token: JWT token as a string.
    """
    BLACKLISTED_TOKENS.add(token)


def extract_token_from_header(auth_header):
    """
    Extract the token from the Authorization header.

    :param auth_header: The Authorization header value.
    :return: JWT token as a string.
    :raises: Unauthorized if the header is missing or invalid.
    """
    if not auth_header or not auth_header.startswith('Bearer '):
        raise Unauthorized("Missing or invalid Authorization header.")
    return auth_header.split(" ")[1]


def refresh_token(old_token):
    """
    Refresh a JWT token by generating a new token with the same payload.

    :param old_token: The old JWT token to refresh.
    :return: A new JWT token as a string.
    :raises: Unauthorized if the old token is invalid or expired.
    """
    decoded_payload = decode_token(old_token)
    # Remove 'exp' from the payload if present to avoid conflicts
    decoded_payload.pop('exp', None)
    return generate_token(decoded_payload)