from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.delivery import DeliveryAgent, Delivery
from app.models.order import Order
from app.models.user import User
from app.utils.auth import role_required
from datetime import datetime

delivery_bp = Blueprint('delivery', __name__)


# ── GET ALL AVAILABLE AGENTS (admin) ─────────────────────────
@delivery_bp.route('/agents', methods=['GET'])
@role_required('admin')
def get_agents():
    agents = DeliveryAgent.query.all()
    return jsonify({'agents': [a.to_dict() for a in agents]}), 200


# ── REGISTER AS DELIVERY AGENT (delivery role user) ──────────
@delivery_bp.route('/agents/register', methods=['POST'])
@role_required('delivery')
def register_agent():
    user_id = int(get_jwt_identity())
    data    = request.get_json()

    if not data.get('vehicle_number'):
        return jsonify({'error': 'vehicle_number is required'}), 400

    existing = DeliveryAgent.query.filter_by(user_id=user_id).first()
    if existing:
        return jsonify({'error': 'Already registered as delivery agent'}), 409

    agent = DeliveryAgent(
        user_id        = user_id,
        vehicle_number = data['vehicle_number'],
        is_available   = True
    )
    db.session.add(agent)
    db.session.commit()
    return jsonify({'message': 'Registered as delivery agent',
                    'agent': agent.to_dict()}), 201


# ── ASSIGN ORDER TO AGENT (admin) ────────────────────────────
@delivery_bp.route('/assign', methods=['POST'])
@role_required('admin')
def assign_delivery():
    data = request.get_json()

    if not data.get('order_id') or not data.get('agent_id'):
        return jsonify({'error': 'order_id and agent_id are required'}), 400

    order = Order.query.get_or_404(data['order_id'])
    agent = DeliveryAgent.query.get_or_404(data['agent_id'])

    # Check if delivery already assigned
    existing = Delivery.query.filter_by(order_id=order.order_id).first()
    if existing:
        return jsonify({'error': 'Delivery already assigned for this order'}), 409

    if not agent.is_available:
        return jsonify({'error': 'Agent is not available'}), 400

    delivery = Delivery(
        order_id = order.order_id,
        agent_id = agent.agent_id,
        status   = 'assigned'
    )
    # Mark agent as unavailable and order as out for delivery
    agent.is_available = False
    order.status       = 'out_for_delivery'

    db.session.add(delivery)
    db.session.commit()
    return jsonify({'message': 'Delivery assigned successfully',
                    'delivery': delivery.to_dict()}), 201


# ── UPDATE DELIVERY STATUS (delivery agent) ───────────────────
@delivery_bp.route('/<int:delivery_id>/status', methods=['PUT'])
@role_required('delivery', 'admin')
def update_delivery_status(delivery_id):
    delivery = Delivery.query.get_or_404(delivery_id)
    data     = request.get_json()

    allowed = ['assigned', 'picked_up', 'on_the_way', 'delivered', 'failed']
    new_status = data.get('status')

    if new_status not in allowed:
        return jsonify({'error': f'Invalid status. Choose from: {allowed}'}), 400

    delivery.status = new_status

    # When delivered — update order, free up agent, record time
    if new_status == 'delivered':
        delivery.delivered_at        = datetime.utcnow()
        delivery.order.status        = 'delivered'
        delivery.agent.is_available  = True

    # When failed — free up agent too
    if new_status == 'failed':
        delivery.agent.is_available  = True
        delivery.order.status        = 'cancelled'

    db.session.commit()
    return jsonify({'message': f'Delivery status updated to {new_status}',
                    'delivery': delivery.to_dict()}), 200


# ── GET MY DELIVERIES (delivery agent) ───────────────────────
@delivery_bp.route('/my', methods=['GET'])
@role_required('delivery')
def my_deliveries():
    user_id = int(get_jwt_identity())
    agent   = DeliveryAgent.query.filter_by(user_id=user_id).first()
    if not agent:
        return jsonify({'error': 'Not registered as delivery agent'}), 404

    deliveries = Delivery.query.filter_by(agent_id=agent.agent_id)\
                               .order_by(Delivery.assigned_at.desc()).all()
    return jsonify({'deliveries': [d.to_dict() for d in deliveries]}), 200


# ── GET DELIVERY FOR AN ORDER ─────────────────────────────────
@delivery_bp.route('/order/<int:order_id>', methods=['GET'])
@jwt_required()
def get_delivery_by_order(order_id):
    delivery = Delivery.query.filter_by(order_id=order_id).first()
    if not delivery:
        return jsonify({'error': 'No delivery found for this order'}), 404
    return jsonify({'delivery': delivery.to_dict()}), 200


# ── TOGGLE AGENT AVAILABILITY ─────────────────────────────────
@delivery_bp.route('/agents/availability', methods=['PUT'])
@role_required('delivery')
def toggle_availability():
    user_id = int(get_jwt_identity())
    agent   = DeliveryAgent.query.filter_by(user_id=user_id).first()
    if not agent:
        return jsonify({'error': 'Not registered as delivery agent'}), 404

    agent.is_available = not agent.is_available
    db.session.commit()
    status = 'available' if agent.is_available else 'unavailable'
    return jsonify({'message': f'You are now {status}',
                    'is_available': agent.is_available}), 200