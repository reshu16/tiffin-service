from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.payment import Payment
from app.models.order import Order
from app.utils.auth import role_required
from datetime import datetime

payment_bp = Blueprint('payment', __name__)


# ── CREATE PAYMENT RECORD (customer places order) ────────────
@payment_bp.route('/create', methods=['POST'])
@jwt_required()
def create_payment():
    user_id = int(get_jwt_identity())
    data    = request.get_json()

    if not data.get('order_id'):
        return jsonify({'error': 'order_id is required'}), 400

    order = Order.query.get_or_404(data['order_id'])

    if order.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    existing = Payment.query.filter_by(order_id=order.order_id).first()
    if existing:
        return jsonify({'error': 'Payment already exists for this order',
                        'payment': existing.to_dict()}), 409

    payment = Payment(
        order_id = order.order_id,
        amount   = order.total_amount,
        method   = data.get('method', 'razorpay'),
        status   = 'pending'
    )
    db.session.add(payment)
    db.session.commit()
    return jsonify({'message': 'Payment record created',
                    'payment': payment.to_dict()}), 201


# ── CONFIRM PAYMENT (after Razorpay success) ─────────────────
@payment_bp.route('/confirm', methods=['POST'])
@jwt_required()
def confirm_payment():
    data = request.get_json()

    if not data.get('order_id') or not data.get('transaction_id'):
        return jsonify({'error': 'order_id and transaction_id are required'}), 400

    payment = Payment.query.filter_by(order_id=data['order_id']).first()
    if not payment:
        return jsonify({'error': 'Payment record not found'}), 404

    payment.status         = 'paid'
    payment.transaction_id = data['transaction_id']
    payment.paid_at        = datetime.utcnow()

    # Auto confirm the order
    payment.order.status = 'confirmed'

    db.session.commit()
    return jsonify({'message': 'Payment confirmed successfully',
                    'payment': payment.to_dict()}), 200


# ── CASH ON DELIVERY ──────────────────────────────────────────
@payment_bp.route('/cod', methods=['POST'])
@jwt_required()
def cod_payment():
    user_id = int(get_jwt_identity())
    data    = request.get_json()

    if not data.get('order_id'):
        return jsonify({'error': 'order_id is required'}), 400

    order = Order.query.get_or_404(data['order_id'])
    if order.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    existing = Payment.query.filter_by(order_id=order.order_id).first()
    if existing:
        return jsonify({'error': 'Payment already exists'}), 409

    payment = Payment(
        order_id = order.order_id,
        amount   = order.total_amount,
        method   = 'cod',
        status   = 'pending'
    )
    order.status = 'confirmed'

    db.session.add(payment)
    db.session.commit()
    return jsonify({'message': 'Cash on delivery confirmed',
                    'payment': payment.to_dict()}), 201


# ── GET PAYMENT FOR AN ORDER ──────────────────────────────────
@payment_bp.route('/order/<int:order_id>', methods=['GET'])
@jwt_required()
def get_payment(order_id):
    payment = Payment.query.filter_by(order_id=order_id).first()
    if not payment:
        return jsonify({'error': 'No payment found for this order'}), 404
    return jsonify({'payment': payment.to_dict()}), 200


# ── GET ALL PAYMENTS (admin) ──────────────────────────────────
@payment_bp.route('/all', methods=['GET'])
@role_required('admin')
def all_payments():
    payments = Payment.query.order_by(Payment.created_at.desc()).all()
    return jsonify({'payments': [p.to_dict() for p in payments]}), 200


# ── REFUND PAYMENT (admin) ────────────────────────────────────
@payment_bp.route('/<int:payment_id>/refund', methods=['PUT'])
@role_required('admin')
def refund_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    if payment.status != 'paid':
        return jsonify({'error': 'Only paid payments can be refunded'}), 400

    payment.status       = 'refunded'
    payment.order.status = 'cancelled'
    db.session.commit()
    return jsonify({'message': 'Payment refunded successfully',
                    'payment': payment.to_dict()}), 200