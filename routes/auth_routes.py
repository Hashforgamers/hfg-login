import time
from flask import Blueprint, request, jsonify, current_app
from services.auth_services import invalidate_token
from utils.jwt_helper import create_jwt_token
from flask_mail import Message
from datetime import datetime, timedelta
from app.extension import mail,db
from models.passwordResetCode import PasswordResetCode
from models.vendorAccount import VendorAccount
from models.vendorPin import VendorPin
from models.vendor import Vendor
from models.passwordManager import PasswordManager
from models.console import Console
from sqlalchemy import func, text
from sqlalchemy import and_
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth', __name__)
_PASSWORD_FLAG_COLUMN_READY = False


def _ensure_password_force_change_column() -> None:
    global _PASSWORD_FLAG_COLUMN_READY
    if _PASSWORD_FLAG_COLUMN_READY:
        return

    try:
        db.session.execute(
            text(
                """
                ALTER TABLE password_manager
                ADD COLUMN IF NOT EXISTS must_change_password BOOLEAN NOT NULL DEFAULT FALSE;
                """
            )
        )
        db.session.commit()
        _PASSWORD_FLAG_COLUMN_READY = True
    except Exception as exc:
        db.session.rollback()
        current_app.logger.warning("password_manager.must_change_password ensure failed: %s", exc)


def _verify_password(stored_password: str, provided_password: str) -> bool:
    if not stored_password:
        return False
    if stored_password == provided_password:
        return True
    try:
        return check_password_hash(stored_password, provided_password)
    except Exception:
        return False


def _verify_pin(stored_pin: str, provided_pin: str) -> bool:
    if not stored_pin:
        return False
    if stored_pin == provided_pin:
        return True
    try:
        return check_password_hash(stored_pin, provided_pin)
    except Exception:
        return False

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

# ─────────────────────────────────────────────────────────────
# HEALTH CHECK — For UptimeRobot monitoring
# GET /api/health
# ─────────────────────────────────────────────────────────────
@auth_bp.route('/health', methods=['GET'])
def auth_health():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({
            "status": "ok",
            "service": "auth",
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "service": "auth",
            "message": str(e)
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login_route():
    _ensure_password_force_change_column()
    started_at = time.perf_counter()
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or "").strip().lower()
    password = (data.get('password') or "").strip()
    parent_type = data.get('parent_type', 'user')

    if not email or not password:
        return jsonify({'status': 'fail', 'message': 'Email and password are required.'}), 400

    if parent_type == 'vendor':
        vendor_account = (
            VendorAccount.query
            .filter(func.lower(VendorAccount.email) == email)
            .first()
        )
        if not vendor_account:
            return jsonify({'status': 'fail', 'message': 'Invalid credentials.'}), 401

        password_row = (
            PasswordManager.query
            .join(
                Vendor,
                and_(
                    Vendor.id == PasswordManager.parent_id,
                    PasswordManager.parent_type == 'vendor'
                )
            )
            .filter(
                Vendor.account_id == vendor_account.id
            )
            .with_entities(
                PasswordManager.password,
                PasswordManager.must_change_password,
            )
            .first()
        )
    else:
        return jsonify({'status': 'fail', 'message': 'User login not implemented yet.'}), 400

    stored_password = password_row.password if password_row else None
    if not _verify_password(stored_password, password):
        return jsonify({'status': 'fail', 'message': 'Invalid credentials.'}), 401

    if password_row and bool(password_row.must_change_password):
        return jsonify({
            'status': 'password_change_required',
            'message': 'Temporary password detected. Please set a new password to continue.',
            'email': email,
        }), 200

    vendor_rows = (
        Vendor.query
        .outerjoin(
            Console,
            and_(
                Console.vendor_id == Vendor.id,
                func.lower(Console.console_type) == 'pc'
            )
        )
        .filter(Vendor.account_id == vendor_account.id)
        .with_entities(
            Vendor.id,
            Vendor.cafe_name,
            Vendor.owner_name,
            Vendor.description,
            func.count(Console.id).label("pc_count"),
        )
        .group_by(Vendor.id, Vendor.cafe_name, Vendor.owner_name, Vendor.description)
        .all()
    )

    vendor_list = [{
        'id': row.id,
        'cafe_name': row.cafe_name,
        'owner_name': row.owner_name,
        'description': row.description,
        'pc_count': int(row.pc_count or 0),
    } for row in vendor_rows]

    response = jsonify({
        'status': 'success',
        'message': 'Login successful.',
        'vendors': vendor_list
    })
    response.headers["X-Response-Time-ms"] = f"{(time.perf_counter() - started_at) * 1000:.2f}"

    current_app.logger.info(
        "login vendor success email=%s vendors=%s latency_ms=%.2f",
        email,
        len(vendor_list),
        (time.perf_counter() - started_at) * 1000,
    )

    return response, 200

@auth_bp.route('/validatePin', methods=['POST'])
def validate_pin():
    started_at = time.perf_counter()
    data = request.get_json(silent=True) or {}
    vendor_id_raw = data.get('vendor_id')
    pin = str(data.get('pin') or "").strip()

    try:
        vendor_id = int(vendor_id_raw)
    except (TypeError, ValueError):
        vendor_id = None

    if not vendor_id or not pin:
        return jsonify({'status': 'fail', 'message': 'vendor_id and pin are required.'}), 400

    if len(pin) < 4 or len(pin) > 10:
        return jsonify({'status': 'fail', 'message': 'Invalid vendor ID or PIN.'}), 401

    pin_row = (
        VendorPin.query
        .join(Vendor, Vendor.id == VendorPin.vendor_id)
        .outerjoin(VendorAccount, VendorAccount.id == Vendor.account_id)
        .with_entities(
            VendorPin.pin_code,
            Vendor.id.label("vendor_id"),
            VendorAccount.email.label("email"),
        )
        .filter(VendorPin.vendor_id == vendor_id)
        .first()
    )

    if not pin_row or not _verify_pin(pin_row.pin_code, pin):
        return jsonify({'status': 'fail', 'message': 'Invalid vendor ID or PIN.'}), 401

    token = create_jwt_token(identity={
        'id': pin_row.vendor_id,
        'type': 'vendor',
        'email': pin_row.email
    })

    response = jsonify({
        'status': 'success',
        'message': 'PIN validated successfully.',
        'data': {
            'token': token,
            'expires_in': 3600 * 4
        }
    })
    response.headers["X-Response-Time-ms"] = f"{(time.perf_counter() - started_at) * 1000:.2f}"

    current_app.logger.info(
        "validatePin success vendor_id=%s latency_ms=%.2f",
        vendor_id,
        (time.perf_counter() - started_at) * 1000,
    )

    return response, 200


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


# ─────────────────────────────────────────────────────────────
# STEP 1: Vendor submits email → OTP sent
# POST /api/forgot-password
# Body: { "email": "vendor@example.com" }
# ─────────────────────────────────────────────────────────────
@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data  = request.get_json()
    email = data.get('email', '').strip().lower()

    if not email:
        return jsonify({'status': 'fail', 'message': 'Email is required.'}), 400

    vendor_account = VendorAccount.query.filter_by(email=email).first()

    # Always return success — never reveal if email exists (security)
    if not vendor_account:
        return jsonify({
            'status': 'success',
            'message': 'If this email is registered, a reset code has been sent.'
        }), 200

    # Invalidate all previous unused codes for this account
    PasswordResetCode.query.filter_by(
        account_id=vendor_account.id,
        is_used=False
    ).update({'is_used': True})
    db.session.flush()

    # Generate new 6-digit OTP, valid for 10 minutes
    code       = PasswordResetCode.generate_code()
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    reset_entry = PasswordResetCode(
        account_id = vendor_account.id,
        code       = code,
        expires_at = expires_at
    )
    db.session.add(reset_entry)
    db.session.commit()

    # Send OTP email via SMTP2GO
    try:
        msg = Message(
            subject    = 'HashForGamers – Password Reset Code',
            recipients = [vendor_account.email]
        )
        msg.html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 480px; 
                    margin: auto; padding: 24px; background: #f9f9f9; 
                    border-radius: 10px;">
            <h2 style="color: #1a1a2e;">🎮 HashForGamers</h2>
            <p>Hi <strong>{vendor_account.name or 'Vendor'}</strong>,</p>
            <p>We received a request to reset your password. 
               Use the code below — it expires in <strong>10 minutes</strong>.</p>
            <div style="font-size: 40px; font-weight: bold; letter-spacing: 10px;
                        color: #4F46E5; background: #fff; padding: 20px;
                        border-radius: 8px; text-align: center; 
                        border: 2px dashed #4F46E5; margin: 20px 0;">
                {code}
            </div>
            <p style="color: #666; font-size: 13px;">
                If you did not request this, ignore this email. 
                Your password will remain unchanged.
            </p>
        </div>
        """
        mail.send(msg)
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'fail', 'message': f'Failed to send email: {str(e)}'}), 500

    return jsonify({
        'status'  : 'success',
        'message' : 'A 6-digit reset code has been sent to your email.'
    }), 200


# ─────────────────────────────────────────────────────────────
# STEP 2: Vendor submits email + OTP → validate
# POST /api/verify-reset-code
# Body: { "email": "vendor@example.com", "code": "123456" }
# ─────────────────────────────────────────────────────────────
@auth_bp.route('/verify-reset-code', methods=['POST'])
def verify_reset_code():
    data  = request.get_json()
    email = data.get('email', '').strip().lower()
    code  = data.get('code', '').strip()

    if not email or not code:
        return jsonify({'status': 'fail', 'message': 'Email and code are required.'}), 400

    vendor_account = VendorAccount.query.filter_by(email=email).first()
    if not vendor_account:
        return jsonify({'status': 'fail', 'message': 'Invalid email or code.'}), 400

    reset_entry = (
        PasswordResetCode.query
        .filter_by(account_id=vendor_account.id, code=code, is_used=False)
        .order_by(PasswordResetCode.created_at.desc())
        .first()
    )

    if not reset_entry or not reset_entry.is_valid():
        return jsonify({
            'status' : 'fail',
            'message': 'Invalid or expired code. Please request a new one.'
        }), 400

    return jsonify({
        'status' : 'success',
        'message': 'Code verified. You may now reset your password.'
    }), 200


# ─────────────────────────────────────────────────────────────
# STEP 3: Vendor submits email + code + new password
# POST /api/reset-password
# Body: { "email": "...", "code": "...", 
#         "new_password": "...", "confirm_password": "..." }
# ─────────────────────────────────────────────────────────────
@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    _ensure_password_force_change_column()
    data             = request.get_json()
    email            = data.get('email', '').strip().lower()
    code             = data.get('code', '').strip()
    new_password     = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')

    if not all([email, code, new_password, confirm_password]):
        return jsonify({'status': 'fail', 'message': 'All fields are required.'}), 400

    if new_password != confirm_password:
        return jsonify({'status': 'fail', 'message': 'Passwords do not match.'}), 400

    if len(new_password) < 8:
        return jsonify({'status': 'fail', 'message': 'Password must be at least 8 characters.'}), 400

    vendor_account = VendorAccount.query.filter_by(email=email).first()
    if not vendor_account:
        return jsonify({'status': 'fail', 'message': 'Invalid request.'}), 400

    reset_entry = (
        PasswordResetCode.query
        .filter_by(account_id=vendor_account.id, code=code, is_used=False)
        .order_by(PasswordResetCode.created_at.desc())
        .first()
    )

    if not reset_entry or not reset_entry.is_valid():
        return jsonify({
            'status' : 'fail',
            'message': 'Invalid or expired code. Please start over.'
        }), 400

    # Update password for ALL vendors under this account via PasswordManager
    vendors = vendor_account.vendors
    for vendor in vendors:
        pm = PasswordManager.query.filter_by(
            parent_id   = vendor.id,
            parent_type = 'vendor'
        ).first()
        if pm:
            pm.password = new_password   # plain text to match your current system
            pm.must_change_password = False
            # ↑ Once you add hashing: generate_password_hash(new_password)

    reset_entry.is_used = True
    db.session.commit()

    return jsonify({
        'status' : 'success',
        'message': 'Password reset successfully. Please login.'
    }), 200


@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    _ensure_password_force_change_column()
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')
    parent_type = (data.get('parent_type') or 'vendor').strip().lower()

    if parent_type != "vendor":
        return jsonify({'status': 'fail', 'message': 'Only vendor password change is supported.'}), 400

    if not all([email, current_password, new_password, confirm_password]):
        return jsonify({'status': 'fail', 'message': 'All fields are required.'}), 400

    if new_password != confirm_password:
        return jsonify({'status': 'fail', 'message': 'Passwords do not match.'}), 400

    if len(new_password) < 8:
        return jsonify({'status': 'fail', 'message': 'Password must be at least 8 characters.'}), 400

    vendor_account = (
        VendorAccount.query
        .filter(func.lower(VendorAccount.email) == email)
        .first()
    )
    if not vendor_account:
        return jsonify({'status': 'fail', 'message': 'Invalid credentials.'}), 401

    rows = (
        PasswordManager.query
        .join(
            Vendor,
            and_(
                Vendor.id == PasswordManager.parent_id,
                PasswordManager.parent_type == 'vendor'
            )
        )
        .filter(Vendor.account_id == vendor_account.id)
        .all()
    )
    if not rows:
        return jsonify({'status': 'fail', 'message': 'Invalid credentials.'}), 401

    if not _verify_password(rows[0].password, current_password):
        return jsonify({'status': 'fail', 'message': 'Current password is incorrect.'}), 401

    for row in rows:
        row.password = new_password
        row.must_change_password = False

    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': 'Password updated successfully. Please login again.'
    }), 200
