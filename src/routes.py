from flask import Blueprint
from src.controllers.user_controller import users
from src.controllers.product_controller import products
from src.controllers.cart_controller import carts
from src.controllers.order_controller import orders

api = Blueprint("api", __name__)
api.register_blueprint(users, url_prefix="/users")
api.register_blueprint(products, url_prefix="/products")
api.register_blueprint(carts, url_prefix="/carts")
api.register_blueprint(orders, url_prefix="/orders")