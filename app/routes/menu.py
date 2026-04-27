from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app import db
from app.models.menu import MenuItem
from app.utils.auth import role_required

menu_bp = Blueprint('menu', __name__)


# ── GET ALL MENU ITEMS (public) ───────────────────────────────
@menu_bp.route('/', methods=['GET'])
def get_menu():
    category = request.args.get('category')  # optional filter
    if category:
        items = MenuItem.query.filter_by(category=category, is_available=True).all()
    else:
        items = MenuItem.query.filter_by(is_available=True).all()
    return jsonify({'menu': [i.to_dict() for i in items]}), 200


# ── GET SINGLE ITEM ───────────────────────────────────────────
@menu_bp.route('/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    return jsonify({'item': item.to_dict()}), 200


# ── ADD MENU ITEM (admin / kitchen only) ─────────────────────
@menu_bp.route('/', methods=['POST'])
@role_required('admin', 'kitchen')
def add_item():
    data = request.get_json()

    required = ['name', 'price', 'category']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    item = MenuItem(
        name         = data['name'],
        description  = data.get('description', ''),
        price        = data['price'],
        category     = data['category'],
        image_url    = data.get('image_url', ''),
        is_available = data.get('is_available', True)
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({'message': 'Menu item added', 'item': item.to_dict()}), 201


# ── UPDATE MENU ITEM (admin / kitchen only) ───────────────────
@menu_bp.route('/<int:item_id>', methods=['PUT'])
@role_required('admin', 'kitchen')
def update_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    data = request.get_json()

    if data.get('name'):         item.name         = data['name']
    if data.get('description'):  item.description  = data['description']
    if data.get('price'):        item.price        = data['price']
    if data.get('category'):     item.category     = data['category']
    if data.get('image_url'):    item.image_url    = data['image_url']
    if 'is_available' in data:   item.is_available = data['is_available']

    db.session.commit()
    return jsonify({'message': 'Menu item updated', 'item': item.to_dict()}), 200


# ── DELETE MENU ITEM (admin only) ─────────────────────────────
@menu_bp.route('/<int:item_id>', methods=['DELETE'])
@role_required('admin')
def delete_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Menu item deleted'}), 200


# ── GET ALL ITEMS INCLUDING UNAVAILABLE (admin/kitchen) ───────
@menu_bp.route('/all', methods=['GET'])
@role_required('admin', 'kitchen')
def get_all_items():
    items = MenuItem.query.all()
    return jsonify({'menu': [i.to_dict() for i in items]}), 200