from flask import Blueprint, render_template, redirect, url_for

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def index():
    return render_template('index.html')

@views_bp.route('/login')
def login():
    return render_template('auth/login.html')

@views_bp.route('/register')
def register():
    return render_template('auth/register.html')

@views_bp.route('/menu')
def menu():
    return render_template('customer/menu.html')

@views_bp.route('/plans')
def plans():
    return render_template('customer/plans.html')

@views_bp.route('/dashboard')
def dashboard():
    return render_template('customer/dashboard.html')

@views_bp.route('/orders')
def orders():
    return render_template('customer/orders.html')

@views_bp.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin/dashboard.html')

@views_bp.route('/kitchen/dashboard')
def kitchen_dashboard():
    return render_template('kitchen/dashboard.html')

@views_bp.route('/delivery/dashboard')
def delivery_dashboard():
    return render_template('delivery/dashboard.html')