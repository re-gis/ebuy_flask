"""
    ___ admin ____
-> create the product
-> delete the product
-> update the product

    ___ client ___
-> get the product
-> get all products
"""


from flask import Blueprint, request, Response, json
from src.middlewares.protected_middleware import token_required

products = Blueprint("products", __name__)

@products.route("/add", methods=["POST"])
@token_required
def addProduct(user):
    print(user)
