from app import db
from datetime import datetime

class Payment(db.Model):
    __tablename__ = 'payments'

    payment_id        = db.Column(db.Integer,      primary_key=True, autoincrement=True)
    order_id          = db.Column(db.Integer,      db.ForeignKey('orders.order_id'),
                                  nullable=False, unique=True)
    amount            = db.Column(db.Numeric(10,2),nullable=False)
    method            = db.Column(db.Enum('razorpay','upi','cod','wallet'),
                                  nullable=False, default='razorpay')
    status            = db.Column(db.Enum('pending','paid','failed','refunded'),
                                  nullable=False, default='pending')
    transaction_id    = db.Column(db.String(200),  nullable=True)
    razorpay_order_id = db.Column(db.String(200),  nullable=True)
    paid_at           = db.Column(db.DateTime,     nullable=True)
    created_at        = db.Column(db.DateTime,     default=datetime.utcnow)

    def to_dict(self):
        return {
            'payment_id':     self.payment_id,
            'order_id':       self.order_id,
            'amount':         float(self.amount),
            'method':         self.method,
            'status':         self.status,
            'transaction_id': self.transaction_id,
            'paid_at':        self.paid_at.isoformat() if self.paid_at else None
        }


class Review(db.Model):
    __tablename__ = 'reviews'

    review_id  = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.user_id'),  nullable=False)
    order_id   = db.Column(db.Integer, db.ForeignKey('orders.order_id'),nullable=False)
    rating     = db.Column(db.Integer, nullable=False)
    comment    = db.Column(db.Text,    nullable=True)
    created_at = db.Column(db.DateTime,default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id','order_id', name='uq_review'),)

    def to_dict(self):
        return {
            'review_id':  self.review_id,
            'user_id':    self.user_id,
            'order_id':   self.order_id,
            'rating':     self.rating,
            'comment':    self.comment,
            'created_at': self.created_at.isoformat()
        }