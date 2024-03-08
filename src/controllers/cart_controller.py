from flask import request, Response, json, Blueprint
from src.middlewares.protected_middleware import token_required
from src.models.models import CartItems, Carts, Product
from src import db


carts = Blueprint("carts", __name__)


@carts.route("/add", methods=["POST"])
@token_required
def addToCart(user):
    try:
        required_fields = ["product_id", "quantity"]
        if all(field in request.json for field in required_fields):
            data = request.json
            product = Product.query.get(data["product_id"])

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

            if data["quantity"] > product.stock:
                return Response(
                    response=json.dumps(
                        {
                            "status": "failed",
                            "message": "Not enough stock!",
                        }
                    ),
                    status=400,
                    mimetype="application/json",
                )

            cart = Carts.query.filter_by(owner_id=user["user_id"]).first()
            if not cart:
                return Response(
                    response=json.dumps(
                        {
                            "status": "not found",
                            "message": "Cart not found!",
                        }
                    ),
                    status=404,
                    mimetype="application/json",
                )

            # Check if the product already exists in the cart
            cart_item = CartItems.query.filter_by(
                cart_id=cart.id, product_name=product.name
            ).first()

            if cart_item:
                # Update the quantity and total price of the existing cart item
                cart_item.quantity += data["quantity"]
                cart_item.total_price = cart_item.quantity * product.price
            else:
                # Create a new cart item and add it to the cart
                cart_item = CartItems(
                    product_name=product.name,
                    quantity=data["quantity"],
                    total_price=data["quantity"] * product.price,
                    cart_id=cart.id,
                )
                db.session.add(cart_item)

            # Update the total quantity and total price of the cart
            cart.total_quantity += data["quantity"]
            cart.total_price += data["quantity"] * product.price

            db.session.commit()

            # Retrieve all cart items for this cart
            cart_items = CartItems.query.filter_by(cart_id=cart.id).all()

            # Construct the response
            response_data = {
                "status": "success",
                "message": "Item(s) added to cart successfully!",
                "cart": {
                    "cart_id": cart.id,
                    "owner": {
                        "user_id": cart.owner.id,
                        "name": cart.owner.username,
                        "email": cart.owner.email,
                    },
                    "cart_items": [
                        {
                            "product_name": item.product_name,
                            "quantity": item.quantity,
                            "price": product.price,
                            "total_price": item.total_price,
                        }
                        for item in cart_items
                    ],
                    "total_quantity": cart.total_quantity,
                    "total_price": cart.total_price,
                },
            }

            return Response(
                response=json.dumps(response_data),
                status=201,
                mimetype="application/json",
            )
        else:
            return Response(
                response=json.dumps(
                    {
                        "status": "bad request",
                        "message": "All cart details are required!",
                    }
                ),
                status=400,
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
