from flask import Blueprint, request, jsonify
from services.auth_services import login, invalidate_token
from utils.jwt_helper import decode_token  # For decoding token if needed
from models.vendorAccount import VendorAccount
from models.vendorPin import VendorPin
from models.passwordManager import PasswordManager

auth_bp = Blueprint('auth', __name__)

# @auth_bp.route('/login', methods=['POST'])
# def login_route():
#     data = request.json
#     email = data.get('email')
#     password = data.get('password')
#     parent_type = data.get('parent_type', 'user')

#     # Validate input
#     if not email or not password:
#         return jsonify({
#             'status': 'fail',
#             'message': 'Email and password are required.'
#         }), 400

#     # Attempt login
#     token, error = login(email, password, parent_type)
#     if error:
#         return jsonify({
#             'status': 'fail',
#             'message': 'Invalid credentials. Please check your email and password.'
#         }), 401

#     # Successful response
#     return jsonify({
#         'status': 'success',
#         'message': 'Login successful.',
#         'data': {
#             'token': token,
#             'expires_in': 3600  # Example: token expiration time in seconds
#         }
#     }), 200

@auth_bp.route('/login', methods=['POST'])
def login_route():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    parent_type = data.get('parent_type', 'user')

    if not email or not password:
        return jsonify({'status': 'fail', 'message': 'Email and password are required.'}), 400

    # Query PasswordManager joined with VendorAccount (if vendor) or User
    if parent_type == 'vendor':
        # Find vendor account by email
        vendor_account = VendorAccount.query.filter_by(email=email).first()
        if not vendor_account:
            return jsonify({'status': 'fail', 'message': 'Invalid credentials.'}), 401

        # Find password manager for any vendor under that account
        password_manager = (
            PasswordManager.query
            .join(Vendor, Vendor.id == PasswordManager.parent_id)
            .filter(
                PasswordManager.parent_type == 'vendor',
                Vendor.account_id == vendor_account.id
            )
            .first()
        )
    else:
        # Implement user lookup similarly if needed
        return jsonify({'status': 'fail', 'message': 'User login not implemented yet.'}), 400

    if not password_manager or password_manager.password != password:
        # TODO: replace with hashed password verification
        return jsonify({'status': 'fail', 'message': 'Invalid credentials.'}), 401

    # On successful login: return all vendors associated with this VendorAccount
    vendors = vendor_account.vendors
    vendor_list = [{
        'id': v.id,
        'cafe_name': v.cafe_name,
        'owner_name': v.owner_name,
        'description': v.description
    } for v in vendors]

    return jsonify({
        'status': 'success',
        'message': 'Login successful.',
        'vendors': vendor_list
    }), 200

@auth_bp.route('/validatePin', methods=['POST'])
def validate_pin():
    data = request.json
    vendor_id = data.get('vendor_id')
    pin = data.get('pin')

    if not vendor_id or not pin:
        return jsonify({'status': 'fail', 'message': 'vendor_id and pin are required.'}), 400

    # Find vendor pin
    vendor_pin = VendorPin.query.filter_by(vendor_id=vendor_id, pin_code=pin).first()
    if not vendor_pin:
        return jsonify({'status': 'fail', 'message': 'Invalid vendor ID or PIN.'}), 401

    # If PIN valid, you might want to generate token or proceed with login
    # For example, create a token (dummy example here)
    token, error = generate_token_for_vendor(vendor_id)
    if error:
        return jsonify({'status': 'fail', 'message': error}), 401

    return jsonify({
        'status': 'success',
        'message': 'PIN validated successfully.',
        'data': {
            'token': token,
            'expires_in': 3600  # example expiry
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
