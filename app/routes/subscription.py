from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.subscription import SubscriptionPlan, UserSubscription
from app.utils.auth import role_required
from datetime import date, timedelta

subscription_bp = Blueprint('subscription', __name__)


# ── GET ALL ACTIVE PLANS (public) ────────────────────────────
@subscription_bp.route('/plans', methods=['GET'])
def get_plans():
    plans = SubscriptionPlan.query.filter_by(is_active=True).all()
    return jsonify({'plans': [p.to_dict() for p in plans]}), 200


# ── GET SINGLE PLAN ───────────────────────────────────────────
@subscription_bp.route('/plans/<int:plan_id>', methods=['GET'])
def get_plan(plan_id):
    plan = SubscriptionPlan.query.get_or_404(plan_id)
    return jsonify({'plan': plan.to_dict()}), 200


# ── ADD PLAN (admin only) ─────────────────────────────────────
@subscription_bp.route('/plans', methods=['POST'])
@role_required('admin')
def add_plan():
    data = request.get_json()
    required = ['plan_name', 'duration', 'price']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    plan = SubscriptionPlan(
        plan_name     = data['plan_name'],
        duration      = data['duration'],
        price         = data['price'],
        description   = data.get('description', ''),
        meals_per_day = data.get('meals_per_day', 1)
    )
    db.session.add(plan)
    db.session.commit()
    return jsonify({'message': 'Plan created', 'plan': plan.to_dict()}), 201


# ── SUBSCRIBE TO A PLAN (customer) ───────────────────────────
@subscription_bp.route('/subscribe', methods=['POST'])
@jwt_required()
def subscribe():
    user_id = int(get_jwt_identity())
    data    = request.get_json()

    if not data.get('plan_id'):
        return jsonify({'error': 'plan_id is required'}), 400

    plan = SubscriptionPlan.query.get_or_404(data['plan_id'])

    # Check if already has active subscription
    existing = UserSubscription.query.filter_by(
        user_id=user_id, status='active').first()
    if existing:
        return jsonify({'error': 'You already have an active subscription'}), 409

    # Calculate end date based on plan duration
    start = date.today()
    if plan.duration == 'daily':
        end = start + timedelta(days=1)
    elif plan.duration == 'weekly':
        end = start + timedelta(weeks=1)
    else:  # monthly
        end = start + timedelta(days=30)

    sub = UserSubscription(
        user_id    = user_id,
        plan_id    = plan.plan_id,
        start_date = start,
        end_date   = end,
        status     = 'active'
    )
    db.session.add(sub)
    db.session.commit()
    return jsonify({'message': 'Subscribed successfully', 'subscription': sub.to_dict()}), 201


# ── GET MY SUBSCRIPTIONS (customer) ──────────────────────────
@subscription_bp.route('/my', methods=['GET'])
@jwt_required()
def my_subscriptions():
    user_id = int(get_jwt_identity())
    subs    = UserSubscription.query.filter_by(user_id=user_id).all()
    return jsonify({'subscriptions': [s.to_dict() for s in subs]}), 200


# ── PAUSE SUBSCRIPTION ────────────────────────────────────────
@subscription_bp.route('/<int:sub_id>/pause', methods=['PUT'])
@jwt_required()
def pause_subscription(sub_id):
    user_id = int(get_jwt_identity())
    sub     = UserSubscription.query.get_or_404(sub_id)

    if sub.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    if sub.status != 'active':
        return jsonify({'error': 'Only active subscriptions can be paused'}), 400

    sub.status = 'paused'
    db.session.commit()
    return jsonify({'message': 'Subscription paused', 'subscription': sub.to_dict()}), 200


# ── RESUME SUBSCRIPTION ───────────────────────────────────────
@subscription_bp.route('/<int:sub_id>/resume', methods=['PUT'])
@jwt_required()
def resume_subscription(sub_id):
    user_id = int(get_jwt_identity())
    sub     = UserSubscription.query.get_or_404(sub_id)

    if sub.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    if sub.status != 'paused':
        return jsonify({'error': 'Only paused subscriptions can be resumed'}), 400

    sub.status = 'active'
    db.session.commit()
    return jsonify({'message': 'Subscription resumed', 'subscription': sub.to_dict()}), 200


# ── CANCEL SUBSCRIPTION ───────────────────────────────────────
@subscription_bp.route('/<int:sub_id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_subscription(sub_id):
    user_id = int(get_jwt_identity())
    sub     = UserSubscription.query.get_or_404(sub_id)

    if sub.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    if sub.status == 'cancelled':
        return jsonify({'error': 'Already cancelled'}), 400

    sub.status = 'cancelled'
    db.session.commit()
    return jsonify({'message': 'Subscription cancelled'}), 200


# ── ALL SUBSCRIPTIONS (admin) ─────────────────────────────────
@subscription_bp.route('/all', methods=['GET'])
@role_required('admin')
def all_subscriptions():
    subs = UserSubscription.query.all()
    return jsonify({'subscriptions': [s.to_dict() for s in subs]}), 200