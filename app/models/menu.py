from app import db
from datetime import datetime

class MenuItem(db.Model):
    __tablename__ = 'menu_items'

    item_id      = db.Column(db.Integer,      primary_key=True, autoincrement=True)
    name         = db.Column(db.String(150),  nullable=False)
    description  = db.Column(db.Text,         nullable=True)
    price        = db.Column(db.Numeric(8,2), nullable=False)
    image_url    = db.Column(db.String(255),  nullable=True)
    category     = db.Column(db.Enum('veg','non-veg','special','dessert'),
                             nullable=False, default='veg')
    is_available = db.Column(db.Boolean,      nullable=False, default=True)
    created_at   = db.Column(db.DateTime,     default=datetime.utcnow)
    updated_at   = db.Column(db.DateTime,     default=datetime.utcnow,
                             onupdate=datetime.utcnow)

    order_items  = db.relationship('OrderItem', backref='menu_item', lazy=True)

    def to_dict(self):
        return {
            'item_id':      self.item_id,
            'name':         self.name,
            'description':  self.description,
            'price':        float(self.price),
            'image_url':    self.image_url,
            'category':     self.category,
            'is_available': self.is_available
        }

    def __repr__(self):
        return f'<MenuItem {self.name}>'