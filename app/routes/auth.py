from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from app import db, bcrypt
from app.models.user import User
from app.models.delivery import DeliveryAgent
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)


# ── REGISTER ──────────────────────────────────────────────────
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    required = ['full_name', 'email', 'password', 'phone']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409

    if User.query.filter_by(phone=data['phone']).first():
        return jsonify({'error': 'Phone number already registered'}), 409

    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    user = User(
        full_name     = data['full_name'],
        email         = data['email'].lower().strip(),
        password_hash = hashed_pw,
        phone         = data['phone'],
        address       = data.get('address', ''),
        role          = 'customer'   # new registrations are always customers
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': 'Registration successful',
        'user': user.to_dict()
    }), 201


# ── LOGIN ─────────────────────────────────────────────────────
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=data['email'].lower().strip()).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401

    if not user.is_active:
        return jsonify({'error': 'Account is deactivated. Contact admin.'}), 403

    # Embed role in JWT so every protected route can check it
    additional_claims = {'role': user.role, 'user_id': user.user_id}

    access_token  = create_access_token(
        identity=str(user.user_id),
        additional_claims=additional_claims,
        expires_delta=timedelta(hours=1)
    )
    refresh_token = create_refresh_token(
        identity=str(user.user_id),
        additional_claims=additional_claims,
        expires_delta=timedelta(days=7)
    )

    return jsonify({
        'message':       'Login successful',
        'access_token':  access_token,
        'refresh_token': refresh_token,
        'user':          user.to_dict()
    }), 200


# ── REFRESH TOKEN ─────────────────────────────────────────────
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    claims   = get_jwt()
    new_token = create_access_token(
        identity=identity,
        additional_claims={'role': claims.get('role'), 'user_id': claims.get('user_id')},
        expires_delta=timedelta(hours=1)
    )
    return jsonify({'access_token': new_token}), 200


# ── GET CURRENT USER PROFILE ───────────────────────────────────
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user    = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'user': user.to_dict()}), 200


# ── UPDATE PROFILE ─────────────────────────────────────────────
@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user    = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    if data.get('full_name'): user.full_name = data['full_name']
    if data.get('phone'):     user.phone     = data['phone']
    if data.get('address'):   user.address   = data['address']

    if data.get('new_password'):
        if not data.get('current_password'):
            return jsonify({'error': 'Current password required'}), 400
        if not bcrypt.check_password_hash(user.password_hash, data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 401
        user.password_hash = bcrypt.generate_password_hash(
            data['new_password']).decode('utf-8')

    db.session.commit()
    return jsonify({'message': 'Profile updated', 'user': user.to_dict()}), 200


# ── LOGOUT (client-side token discard) ────────────────────────
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # JWT is stateless — actual logout is done by deleting the token on the frontend
    return jsonify({'message': 'Logged out successfully'}), 200