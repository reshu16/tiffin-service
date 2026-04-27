from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.order import Order, OrderItem
from app.models.menu import MenuItem
from app.utils.auth import role_required
from datetime import datetime

orders_bp = Blueprint('orders', __name__)


# ── PLACE ORDER (customer) ────────────────────────────────────
@orders_bp.route('/', methods=['POST'])
@jwt_required()
def place_order():
    user_id = int(get_jwt_identity())
    data    = request.get_json()

    if not data.get('items') or len(data['items']) == 0:
        return jsonify({'error': 'Order must have at least one item'}), 400
    if not data.get('delivery_address'):
        return jsonify({'error': 'Delivery address is required'}), 400

    total = 0
    order_items = []

    for entry in data['items']:
        item = MenuItem.query.get(entry.get('item_id'))
        if not item:
            return jsonify({'error': f"Item {entry.get('item_id')} not found"}), 404
        if not item.is_available:
            return jsonify({'error': f"'{item.name}' is currently unavailable"}), 400

        qty      = entry.get('quantity', 1)
        subtotal = float(item.price) * qty
        total   += subtotal

        order_items.append(OrderItem(
            item_id    = item.item_id,
            quantity   = qty,
            unit_price = item.price
        ))

    order = Order(
        user_id          = user_id,
        subscription_id  = data.get('subscription_id'),
        total_amount     = round(total, 2),
        delivery_address = data['delivery_address'],
        special_notes    = data.get('special_notes', ''),
        status           = 'pending'
    )
    db.session.add(order)
    db.session.flush()   # get order_id before committing

    for oi in order_items:
        oi.order_id = order.order_id
        db.session.add(oi)

    db.session.commit()
    return jsonify({'message': 'Order placed successfully', 'order': order.to_dict()}), 201


# ── GET MY ORDERS (customer) ──────────────────────────────────
@orders_bp.route('/my', methods=['GET'])
@jwt_required()
def my_orders():
    user_id = int(get_jwt_identity())
    orders  = Order.query.filter_by(user_id=user_id)\
                         .order_by(Order.order_date.desc()).all()
    return jsonify({'orders': [o.to_dict() for o in orders]}), 200


# ── GET SINGLE ORDER ──────────────────────────────────────────
@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    user_id = int(get_jwt_identity())
    claims  = __import__('flask_jwt_extended').get_jwt()
    order   = Order.query.get_or_404(order_id)

    # customers can only see their own orders
    if claims.get('role') == 'customer' and order.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    return jsonify({'order': order.to_dict()}), 200


# ── CANCEL ORDER (customer) ───────────────────────────────────
@orders_bp.route('/<int:order_id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_order(order_id):
    user_id = int(get_jwt_identity())
    order   = Order.query.get_or_404(order_id)

    if order.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    if order.status not in ('pending', 'confirmed'):
        return jsonify({'error': f'Cannot cancel order with status: {order.status}'}), 400

    order.status = 'cancelled'
    db.session.commit()
    return jsonify({'message': 'Order cancelled successfully'}), 200


# ── UPDATE ORDER STATUS (admin / kitchen) ─────────────────────
@orders_bp.route('/<int:order_id>/status', methods=['PUT'])
@role_required('admin', 'kitchen', 'delivery')
def update_status(order_id):
    order = Order.query.get_or_404(order_id)
    data  = request.get_json()

    allowed = ['pending','confirmed','preparing','out_for_delivery','delivered','cancelled']
    new_status = data.get('status')

    if new_status not in allowed:
        return jsonify({'error': f'Invalid status. Choose from: {allowed}'}), 400

    order.status = new_status
    db.session.commit()
    return jsonify({'message': f'Order status updated to {new_status}',
                    'order': order.to_dict()}), 200


# ── GET ALL ORDERS (admin / kitchen) ─────────────────────────
@orders_bp.route('/all', methods=['GET'])
@role_required('admin', 'kitchen')
def all_orders():
    status = request.args.get('status')
    if status:
        orders = Order.query.filter_by(status=status)\
                            .order_by(Order.order_date.desc()).all()
    else:
        orders = Order.query.order_by(Order.order_date.desc()).all()
    return jsonify({'orders': [o.to_dict() for o in orders]}), 200


# ── TODAY'S ORDERS (kitchen dashboard) ───────────────────────
@orders_bp.route('/today', methods=['GET'])
@role_required('admin', 'kitchen')
def todays_orders():
    today   = datetime.utcnow().date()
    orders  = Order.query.filter(
        db.func.date(Order.order_date) == today
    ).order_by(Order.order_date.desc()).all()
    return jsonify({
        'date':   str(today),
        'count':  len(orders),
        'orders': [o.to_dict() for o in orders]
    }), 200

from app.models.payment import Review

# ── SUBMIT REVIEW (customer) ──────────────────────────────────
@orders_bp.route('/<int:order_id>/review', methods=['POST'])
@jwt_required()
def submit_review(order_id):
    user_id = int(get_jwt_identity())
    order   = Order.query.get_or_404(order_id)

    if order.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    if order.status != 'delivered':
        return jsonify({'error': 'Can only review delivered orders'}), 400

    data   = request.get_json()
    rating = data.get('rating')

    if not rating or not (1 <= int(rating) <= 5):
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400

    existing = Review.query.filter_by(
        user_id=user_id, order_id=order_id).first()
    if existing:
        return jsonify({'error': 'Already reviewed this order'}), 409

    review = Review(
        user_id  = user_id,
        order_id = order_id,
        rating   = int(rating),
        comment  = data.get('comment', '')
    )
    db.session.add(review)
    db.session.commit()
    return jsonify({'message': 'Review submitted', 'review': review.to_dict()}), 201