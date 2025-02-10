from flask import Blueprint, request, jsonify
from services.auth_services import login, invalidate_token
from utils.jwt_helper import decode_token  # For decoding token if needed

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login_route():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    parent_type = data.get('parent_type', 'user')

    # Validate input
    if not email or not password:
        return jsonify({
            'status': 'fail',
            'message': 'Email and password are required.'
        }), 400

    # Attempt login
    token, error = login(email, password, parent_type)
    if error:
        return jsonify({
            'status': 'fail',
            'message': 'Invalid credentials. Please check your email and password.'
        }), 401

    # Successful response
    return jsonify({
        'status': 'success',
        'message': 'Login successful.',
        'data': {
            'token': token,
            'expires_in': 3600  # Example: token expiration time in seconds
        }
    }), 200

@auth_bp.route('/logout', methods=['POST'])
def logout_route():
    # Extract the token from the Authorization header
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({
            'status': 'fail',
            'message': 'Token is missing or invalid.'
        }), 401

    # Extract the token
    token = auth_header.split(" ")[1]

    try:
        # Invalidate the token (this might include adding it to a blacklist in production)
        invalidate_token(token)
    except Exception as e:
        return jsonify({
            'status': 'fail',
            'message': 'Failed to log out. Please try again.',
            'error': str(e)  # Optionally omit this for production to avoid exposing details
        }), 500

    # Successful logout
    return jsonify({
        'status': 'success',
        'message': 'Successfully logged out.'
    }), 200
