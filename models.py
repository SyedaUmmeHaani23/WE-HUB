"""
Database models for the Women Entrepreneurs Hub application.
"""
from datetime import datetime
from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    """User model for local database references."""
    id = db.Column(db.Integer, primary_key=True)
    firebase_uid = db.Column(db.String(128), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=True)
    profile_picture = db.Column(db.String(256), nullable=True)
    business_name = db.Column(db.String(120), nullable=True)
    business_description = db.Column(db.Text, nullable=True)
    business_category = db.Column(db.String(64), nullable=True)
    website = db.Column(db.String(256), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(256), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    google_business_id = db.Column(db.String(128), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<User {self.username}>'

class Product(db.Model):
    """Product model for e-commerce."""
    id = db.Column(db.Integer, primary_key=True)
    firebase_id = db.Column(db.String(128), unique=True, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(256), nullable=True)
    category = db.Column(db.String(64), nullable=True)
    stock = db.Column(db.Integer, default=0)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('products', lazy=True))

    def __repr__(self):
        return f'<Product {self.name}>'

class Event(db.Model):
    """Event model for community events and workshops."""
    id = db.Column(db.Integer, primary_key=True)
    firebase_id = db.Column(db.String(128), unique=True, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(256), nullable=True)
    virtual_link = db.Column(db.String(256), nullable=True)
    is_virtual = db.Column(db.Boolean, default=False)
    max_participants = db.Column(db.Integer, nullable=True)
    image_url = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('events', lazy=True))

    def __repr__(self):
        return f'<Event {self.title}>'

class ForumPost(db.Model):
    """Forum post model for community discussions."""
    id = db.Column(db.Integer, primary_key=True)
    firebase_id = db.Column(db.String(128), unique=True, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(64), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('forum_posts', lazy=True))

    def __repr__(self):
        return f'<ForumPost {self.title}>'

class ForumComment(db.Model):
    """Forum comment model for community discussions."""
    id = db.Column(db.Integer, primary_key=True)
    firebase_id = db.Column(db.String(128), unique=True, nullable=True)
    post_id = db.Column(db.Integer, db.ForeignKey('forum_post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    post = db.relationship('ForumPost', backref=db.backref('comments', lazy=True))
    user = db.relationship('User', backref=db.backref('forum_comments', lazy=True))

    def __repr__(self):
        return f'<ForumComment {self.id}>'

class EventRegistration(db.Model):
    """Event registration model for users registering to events."""
    id = db.Column(db.Integer, primary_key=True)
    firebase_id = db.Column(db.String(128), unique=True, nullable=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='registered')  # registered, attended, cancelled

    event = db.relationship('Event', backref=db.backref('registrations', lazy=True))
    user = db.relationship('User', backref=db.backref('event_registrations', lazy=True))

    def __repr__(self):
        return f'<EventRegistration {self.id}>'

class Order(db.Model):
    """Order model for e-commerce purchases."""
    id = db.Column(db.Integer, primary_key=True)
    firebase_id = db.Column(db.String(128), unique=True, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, completed, cancelled
    payment_method = db.Column(db.String(50), nullable=True)
    payment_id = db.Column(db.String(128), nullable=True)
    shipping_address = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('orders', lazy=True))

    def __repr__(self):
        return f'<Order {self.id}>'

class OrderItem(db.Model):
    """Order item model for individual items in an order."""
    id = db.Column(db.Integer, primary_key=True)
    firebase_id = db.Column(db.String(128), unique=True, nullable=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    order = db.relationship('Order', backref=db.backref('items', lazy=True))
    product = db.relationship('Product')

    def __repr__(self):
        return f'<OrderItem {self.id}>'
