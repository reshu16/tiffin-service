from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    user_id       = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name     = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone         = db.Column(db.String(15),  nullable=False, unique=True)
    address       = db.Column(db.Text,        nullable=True)
    role          = db.Column(db.Enum('customer','admin','kitchen','delivery'),
                              nullable=False, default='customer')
    profile_image = db.Column(db.String(255), nullable=True)
    is_active     = db.Column(db.Boolean,     nullable=False, default=True)
    created_at    = db.Column(db.DateTime,    default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime,    default=datetime.utcnow,
                              onupdate=datetime.utcnow)

    # Relationships
    subscriptions   = db.relationship('UserSubscription', backref='user', lazy=True)
    orders          = db.relationship('Order',            backref='user', lazy=True)
    reviews         = db.relationship('Review',           backref='user', lazy=True)
    delivery_agent  = db.relationship('DeliveryAgent',    backref='user',
                                      uselist=False, lazy=True)

    def to_dict(self):
        return {
            'user_id':   self.user_id,
            'full_name': self.full_name,
            'email':     self.email,
            'phone':     self.phone,
            'address':   self.address,
            'role':      self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<User {self.email}>'