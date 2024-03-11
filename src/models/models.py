from flask_sqlalchemy import SQLAlchemy
from src import db
from datetime import datetime


class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=True)

    def __str__(self):
        return self.email


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    stock = db.Column(db.Integer)
    image_url = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)


class Carts(db.Model):
    __tablename__ = "carts"
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    owner = db.relationship("Users", backref="carts", lazy=True)
    cart_items = db.relationship("CartItems", backref="cart", lazy="dynamic")
    total_quantity = db.Column(db.Integer)
    total_price = db.Column(db.Float)


class CartItems(db.Model):
    __tablename__ = "cart_items"
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    cart_id = db.Column(db.Integer, db.ForeignKey("carts.id"))
    total_price = db.Column(db.Float)


class Orders(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("Users", backref="orders", lazy=True)
    location_id = db.Column(db.Integer, db.ForeignKey("locations.id"), nullable=False)
    location = db.relationship("UserLocations", backref="orders", lazy=True)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    order_items = db.relationship("OrderItems", backref="Orders", lazy="dynamic")
    order_date = db.Column(db.DateTime, default=datetime.utcnow)


class OrderItems(db.Model):
    __tablename__ = "order_items"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)


class UserLocations(db.Model):
    __tablename__ = "locations"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("Users", backref="UserLocations", lazy=True)
    country = db.Column(db.String(100), nullable=False)
    province = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    sector = db.Column(db.String(100), nullable=False)
