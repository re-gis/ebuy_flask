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
            # add to cart and decrease the product stock
            # get the product and update it and also get the user id
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

            # make the cart item
            cartitem = CartItems(
                product_name=product.name, quantity=data["quantity"], cart_id=cart.id
            )

            # update the cart && product
            cart.CartItems = cartitem
            product.stock = product.stock - int(data["quantity"])

            db.session.add(cartitem)
            db.session.commit()

            return Response(
                response=json.dumps(
                    {
                        "status": "success",
                        "message": "Item added to cart successfully!",
                        "cart": cart,
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
