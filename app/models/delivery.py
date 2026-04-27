from app import db
from datetime import datetime

class DeliveryAgent(db.Model):
    __tablename__ = 'delivery_agents'

    agent_id       = db.Column(db.Integer,      primary_key=True, autoincrement=True)
    user_id        = db.Column(db.Integer,      db.ForeignKey('users.user_id'),
                               nullable=False, unique=True)
    vehicle_number = db.Column(db.String(20),   nullable=False)
    is_available   = db.Column(db.Boolean,      nullable=False, default=True)
    rating         = db.Column(db.Numeric(3,2), nullable=False, default=5.00)
    created_at     = db.Column(db.DateTime,     default=datetime.utcnow)

    deliveries = db.relationship('Delivery', backref='agent', lazy=True)

    def to_dict(self):
        return {
            'agent_id':       self.agent_id,
            'user_id':        self.user_id,
            'name':           self.user.full_name if self.user else None,
            'phone':          self.user.phone     if self.user else None,
            'vehicle_number': self.vehicle_number,
            'is_available':   self.is_available,
            'rating':         float(self.rating)
        }


class Delivery(db.Model):
    __tablename__ = 'deliveries'

    delivery_id    = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id       = db.Column(db.Integer, db.ForeignKey('orders.order_id'),
                               nullable=False, unique=True)
    agent_id       = db.Column(db.Integer, db.ForeignKey('delivery_agents.agent_id'),
                               nullable=False)
    status         = db.Column(db.Enum('assigned','picked_up','on_the_way',
                                       'delivered','failed'),
                               nullable=False, default='assigned')
    assigned_at    = db.Column(db.DateTime, default=datetime.utcnow)
    delivered_at   = db.Column(db.DateTime, nullable=True)
    delivery_notes = db.Column(db.Text,     nullable=True)

    def to_dict(self):
        return {
            'delivery_id':  self.delivery_id,
            'order_id':     self.order_id,
            'agent_id':     self.agent_id,
            'agent_name':   self.agent.user.full_name if self.agent else None,
            'status':       self.status,
            'assigned_at':  self.assigned_at.isoformat(),
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None
        }