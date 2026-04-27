from app import db
from datetime import datetime

class SubscriptionPlan(db.Model):
    __tablename__ = 'subscription_plans'

    plan_id       = db.Column(db.Integer,      primary_key=True, autoincrement=True)
    plan_name     = db.Column(db.String(100),  nullable=False)
    duration      = db.Column(db.Enum('daily','weekly','monthly'), nullable=False)
    price         = db.Column(db.Numeric(8,2), nullable=False)
    description   = db.Column(db.Text,         nullable=True)
    meals_per_day = db.Column(db.Integer,      nullable=False, default=1)
    is_active     = db.Column(db.Boolean,      nullable=False, default=True)
    created_at    = db.Column(db.DateTime,     default=datetime.utcnow)

    subscriptions = db.relationship('UserSubscription', backref='plan', lazy=True)

    def to_dict(self):
        return {
            'plan_id':       self.plan_id,
            'plan_name':     self.plan_name,
            'duration':      self.duration,
            'price':         float(self.price),
            'description':   self.description,
            'meals_per_day': self.meals_per_day,
            'is_active':     self.is_active
        }


class UserSubscription(db.Model):
    __tablename__ = 'user_subscriptions'

    subscription_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.user_id'),
                                nullable=False)
    plan_id         = db.Column(db.Integer, db.ForeignKey('subscription_plans.plan_id'),
                                nullable=False)
    start_date      = db.Column(db.Date,    nullable=False)
    end_date        = db.Column(db.Date,    nullable=False)
    status          = db.Column(db.Enum('active','paused','cancelled','expired'),
                                nullable=False, default='active')
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    orders = db.relationship('Order', backref='subscription', lazy=True)

    def to_dict(self):
        return {
            'subscription_id': self.subscription_id,
            'user_id':         self.user_id,
            'plan_id':         self.plan_id,
            'plan_name':       self.plan.plan_name if self.plan else None,
            'start_date':      self.start_date.isoformat(),
            'end_date':        self.end_date.isoformat(),
            'status':          self.status
        }