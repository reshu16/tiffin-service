from app import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'

    order_id         = db.Column(db.Integer,      primary_key=True, autoincrement=True)
    user_id          = db.Column(db.Integer,      db.ForeignKey('users.user_id'),
                                 nullable=False)
    subscription_id  = db.Column(db.Integer,      db.ForeignKey('user_subscriptions.subscription_id'),
                                 nullable=True)
    total_amount     = db.Column(db.Numeric(10,2),nullable=False)
    status           = db.Column(db.Enum('pending','confirmed','preparing',
                                         'out_for_delivery','delivered','cancelled'),
                                 nullable=False, default='pending')
    delivery_address = db.Column(db.Text,         nullable=False)
    special_notes    = db.Column(db.Text,         nullable=True)
    order_date       = db.Column(db.DateTime,     default=datetime.utcnow)
    updated_at       = db.Column(db.DateTime,     default=datetime.utcnow,
                                 onupdate=datetime.utcnow)

    items    = db.relationship('OrderItem', backref='order', lazy=True,
                               cascade='all, delete-orphan')
    delivery = db.relationship('Delivery',  backref='order', uselist=False, lazy=True)
    payment  = db.relationship('Payment',   backref='order', uselist=False, lazy=True)
    reviews  = db.relationship('Review',    backref='order', lazy=True)

    def to_dict(self):
        return {
            'order_id':         self.order_id,
            'user_id':          self.user_id,
            'total_amount':     float(self.total_amount),
            'status':           self.status,
            'delivery_address': self.delivery_address,
            'special_notes':    self.special_notes,
            'order_date':       self.order_date.isoformat(),
            'items':            [i.to_dict() for i in self.items]
        }


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    order_item_id = db.Column(db.Integer,      primary_key=True, autoincrement=True)
    order_id      = db.Column(db.Integer,      db.ForeignKey('orders.order_id'),
                              nullable=False)
    item_id       = db.Column(db.Integer,      db.ForeignKey('menu_items.item_id'),
                              nullable=False)
    quantity      = db.Column(db.Integer,      nullable=False, default=1)
    unit_price    = db.Column(db.Numeric(8,2), nullable=False)

    def to_dict(self):
        return {
            'order_item_id': self.order_item_id,
            'item_id':       self.item_id,
            'item_name':     self.menu_item.name if self.menu_item else None,
            'quantity':      self.quantity,
            'unit_price':    float(self.unit_price),
            'subtotal':      float(self.unit_price * self.quantity)
        }