"""
    ___ admin ____
-> create the product
-> delete the product
-> update the product

    ___ client ___
-> get the product
-> get all products
"""

from flask import Blueprint, request, Response, json, jsonify
from src.middlewares.protected_middleware import token_required
from src.models.models import Product
from datetime import datetime
from src.utils import upload_image
from src import db

products = Blueprint("products", __name__)


@products.route("/add", methods=["POST"])
@token_required
def addProduct(user):
    try:
        if user["role"] not in ["SELLER", "ADMIN"]:
            return Response(
                response=json.dumps(
                    {
                        "status": "Not authorised",
                        "message": "You are not authorised to perform this action!",
                    }
                ),
                status=403,
                mimetype="application/json",
            )

        # Check if all required fields are present in the form data
        required_fields = ["name", "quantity", "description", "price"]
        if all(field in request.form for field in required_fields):
            # Upload the image
            if not request.files["image"]:
                return Response(
                    response=json.dumps(
                        {"status": "bad request", "message": "Image is required!"}
                    ),
                    status=400,
                    mimetype="application/json",
                )
            p = Product.query.filter_by(name=request.form["name"]).first()
            if p:
                return Response(
                    response=json.dumps(
                        {
                            "status": "Bad request",
                            "messsage": "Product already exists, update it instead!",
                        }
                    ),
                    status=400,
                    mimetype="application/json",
                )
            img_object = upload_image(request.files["image"])

            # Create a product
            product = Product(
                name=request.form["name"],
                stock=request.form["quantity"],
                price=request.form["price"],
                description=request.form["description"],
                date_added=datetime.utcnow(),
                image_url=img_object,
            )
            
            product_dict = {
                "name":product.name,
                "description": product.description,
                "stock":product.stock,
                "price":product.price,
                "image":product.image_url,
                "date_added":product.date_added
            }

            db.session.add(product)
            db.session.commit()
            return Response(
                response=json.dumps(
                    {
                        "status": "created",
                        "message": "Product added successfully...",
                        "product": product_dict,
                    }
                ),
                status=201,
                mimetype="application/json",
            )
        else:
            return Response(
                response=json.dumps(
                    {
                        "status": "bad request",
                        "message": "All product details are required!",
                    }
                ),
                status=400,
                mimetype="application/json",
            )

    except Exception as e:
        print(e)
        return Response(
            response=json.dumps(
                {
                    "status": "failed",
                    "message": "Internal server error...",
                    "error": str(e),
                }
            ),
            status=500,
            mimetype="application/json",
        )
