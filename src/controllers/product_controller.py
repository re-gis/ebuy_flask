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
import src.models.models
from datetime import datetime
from src.utils import upload_image
from src import db
from src.controllers.user_controller import bcrypt
from src.models.models import Product, Users

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
                "name": product.name,
                "description": product.description,
                "stock": product.stock,
                "price": product.price,
                "image": product.image_url,
                "date_added": product.date_added,
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


@products.route("/", methods=["GET"])
def getProducts():
    try:
        products = Product.query.all()

        p_list = []

        for product in products:
            product_data = {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "stock": product.stock,
                "image": product.image_url,
                "date added": product.date_added,
            }
            p_list.append(product_data)

        if len(p_list) == 0:
            return Response(
                response=json.dumps({"status": "OK", "message": "No products found!"}),
                status=200,
                mimetype="application/json",
            )
        return Response(
            response=json.dumps({"status": "success", "products": p_list}),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
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


@products.route("/<int:id>", methods=["GET"])
def getProductById(id):
    try:
        # getting the product by id
        product = Product.query.get(id)
        if not product:
            return Response(
                response=json.dumps(
                    {
                        "status": "not found",
                        "message": "Product not found!",
                    }
                ),
                status=404,
                mimetype="application/json",
            )

        product_data = {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "stock": product.stock,
            "image": product.image_url,
            "date added": product.date_added,
        }

        return Response(
            response=json.dumps(
                {
                    "status": "success",
                    "product": product_data,
                }
            ),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
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


@products.route("/update/<int:id>", methods=["PUT"])
@token_required
def updateProduct(user, id):
    try:
        # first check the user's role
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
        # get the product
        product = Product.query.get(id)
        if not product:
            return Response(
                response=json.dumps(
                    {
                        "status": "not found",
                        "message": "Product not found!",
                    }
                ),
                status=404,
                mimetype="application/json",
            )
        data = request.form
        # update the product
        if "name" in data and data["name"] != "":
            product.name = data["name"]
        if "description" in data and data["description"] != "":
            product.description = data["description"]
        if "price" in data and data["price"] != "":
            product.price = data["price"]
        if "quantity" in data and data["quantity"] != "":
            product.stock = data["quantity"]

        if "image" in request.files and request.files["image"] != "":
            uploaded_file = request.files["image"]
            if uploaded_file.filename != "":
                # If an image file is present, upload it
                img_object = upload_image(uploaded_file)
                product.image_url = img_object["url"]

        # Save the updated product
        db.session.commit()

        product_data = {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "stock": product.stock,
            "image": product.image_url,
            "date added": product.date_added,
        }

        return Response(
            response=json.dumps(
                {
                    "status": "success",
                    "message": "Product updated successfully...",
                    "product": product_data,
                }
            ),
            status=201,
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


@products.route("/delete/<int:id>", methods=["DELETE"])
@token_required
def deleteProduct(user, id):
    try:
        if user["role"] != "SELLER" and user["role"] != "ADMIN":
            return Response(
                response=json.dumps(
                    {
                        "status": "forbidden",
                        "message": "You are not authorised to perform this action!",
                    }
                ),
                status=403,
                mimetype="application/json",
            )

        product = Product.query.get(id)
        if not product:
            return Response(
                response=json.dumps(
                    {"status": "not found", "message": "Product not found!"}
                ),
                status=404,
                mimetype="application/json",
            )

        # get password and delete the product
        data = request.json
        if "password" not in data:
            return Response(
                response=json.dumps(
                    {
                        "status": "bad request",
                        "message": "Password is required to delete the product!",
                    }
                ),
                status=400,
                mimetype="application/json",
            )
        # get user
        user = Users.query.filter_by(email=user["email"]).first()
        if not user:
            return Response(
                response=json.dumps(
                    {
                        "status": "not found",
                        "message": "User not found!",
                    }
                ),
                status=404,
                mimetype="application/json",
            )

        # check if the password is valid
        if not bcrypt.check_password_hash(user.password, data["password"]):
            return Response(
                response=json.dumps(
                    {
                        "status": "invalid password",
                        "message": "Incorrect password!",
                    }
                ),
                status=400,
                mimetype="application/json",
            )

        # delete the user
        db.session.delete(product)
        db.session.commit()
        return Response(
            response=json.dumps(
                {
                    "status": "success",
                    "message": "Product deleted successfully...",
                }
            ),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
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
