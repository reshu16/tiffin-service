from flask import Blueprint, request, jsonify
from app import db, bcrypt
from app.models.user import User
from app.models.order import Order
from app.models.payment import Payment
from app.models.delivery import DeliveryAgent
from app.utils.auth import role_required
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)


# ── DASHBOARD STATS ───────────────────────────────────────────
@admin_bp.route('/dashboard', methods=['GET'])
@role_required('admin')
def dashboard():
    today = datetime.utcnow().date()

    total_users      = User.query.filter_by(role='customer').count()
    total_orders     = Order.query.count()
    today_orders     = Order.query.filter(
                           db.func.date(Order.order_date) == today).count()
    pending_orders   = Order.query.filter_by(status='pending').count()
    delivered_orders = Order.query.filter_by(status='delivered').count()
    cancelled_orders = Order.query.filter_by(status='cancelled').count()
    total_revenue    = db.session.query(
                           db.func.sum(Payment.amount)
                       ).filter_by(status='paid').scalar() or 0

    today_revenue    = db.session.query(
                           db.func.sum(Payment.amount)
                       ).filter(
                           Payment.status == 'paid',
                           db.func.date(Payment.paid_at) == today
                       ).scalar() or 0

    available_agents = DeliveryAgent.query.filter_by(is_available=True).count()

    return jsonify({
        'stats': {
            'total_users':      total_users,
            'total_orders':     total_orders,
            'today_orders':     today_orders,
            'pending_orders':   pending_orders,
            'delivered_orders': delivered_orders,
            'cancelled_orders': cancelled_orders,
            'total_revenue':    float(total_revenue),
            'today_revenue':    float(today_revenue),
            'available_agents': available_agents
        }
    }), 200


# ── GET ALL USERS ─────────────────────────────────────────────
@admin_bp.route('/users', methods=['GET'])
@role_required('admin')
def get_users():
    role  = request.args.get('role')
    users = User.query.filter_by(role=role).all() if role \
            else User.query.all()
    return jsonify({'users': [u.to_dict() for u in users]}), 200


# ── CREATE USER (admin creates kitchen/delivery accounts) ─────
@admin_bp.route('/users', methods=['POST'])
@role_required('admin')
def create_user():
    data = request.get_json()
    required = ['full_name', 'email', 'password', 'phone', 'role']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    if data['role'] not in ('admin', 'kitchen', 'delivery', 'customer'):
        return jsonify({'error': 'Invalid role'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409

    hashed = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user   = User(
        full_name     = data['full_name'],
        email         = data['email'].lower().strip(),
        password_hash = hashed,
        phone         = data['phone'],
        role          = data['role'],
        address       = data.get('address', '')
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created', 'user': user.to_dict()}), 201


# ── TOGGLE USER ACTIVE/INACTIVE ───────────────────────────────
@admin_bp.route('/users/<int:user_id>/toggle', methods=['PUT'])
@role_required('admin')
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    status = 'activated' if user.is_active else 'deactivated'
    return jsonify({'message': f'User {status}',
                    'is_active': user.is_active}), 200


# ── REVENUE REPORT (last 7 days) ──────────────────────────────
@admin_bp.route('/reports/revenue', methods=['GET'])
@role_required('admin')
def revenue_report():
    days   = int(request.args.get('days', 7))
    result = []

    for i in range(days):
        day = datetime.utcnow().date() - timedelta(days=i)
        rev = db.session.query(
                  db.func.sum(Payment.amount)
              ).filter(
                  Payment.status == 'paid',
                  db.func.date(Payment.paid_at) == day
              ).scalar() or 0
        orders = Order.query.filter(
                     db.func.date(Order.order_date) == day).count()
        result.append({
            'date':    str(day),
            'revenue': float(rev),
            'orders':  orders
        })

    return jsonify({'report': result}), 200