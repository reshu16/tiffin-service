from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_mail import Mail
from .config import config
from flask import render_template

db     = SQLAlchemy()
jwt    = JWTManager()
bcrypt = Bcrypt()
mail   = Mail()

def create_app(env='default'):
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(config[env])

    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    CORS(app)
    mail.init_app(app)
    from .routes.views import views_bp
    app.register_blueprint(views_bp)

    with app.app_context():
        from app.models import User, MenuItem, SubscriptionPlan, UserSubscription
        from app.models import Order, OrderItem, DeliveryAgent, Delivery
        from app.models import Payment, Review

        from .routes.auth         import auth_bp
        from .routes.menu         import menu_bp
        from .routes.subscription import subscription_bp
        from .routes.orders       import orders_bp
        from .routes.delivery     import delivery_bp
        from .routes.payment      import payment_bp
        from .routes.admin        import admin_bp

        app.register_blueprint(auth_bp,         url_prefix='/api/auth')
        app.register_blueprint(menu_bp,          url_prefix='/api/menu')
        app.register_blueprint(subscription_bp,  url_prefix='/api/subscription')
        app.register_blueprint(orders_bp,        url_prefix='/api/orders')
        app.register_blueprint(delivery_bp,      url_prefix='/api/delivery')
        app.register_blueprint(payment_bp,       url_prefix='/api/payment')
        app.register_blueprint(admin_bp,         url_prefix='/api/admin')

    return app
   

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500