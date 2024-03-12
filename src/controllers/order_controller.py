from datetime import datetime
from flask import request, Response, json, Blueprint
from src import db
from src.middlewares.protected_middleware import token_required
from src.models.models import Carts, OrderItems, Orders, UserLocations
from src.utils import sendEmail


orders = Blueprint("orders", __name__)


@orders.route("/", methods=["POST"])
@token_required
def order(user):
    try:
        if user["role"] != "CLIENT":
            return Response(
                response=json.dumps(
                    {
                        "status": "forbidden",
                        "message": "You are not allowed to perform this action!",
                    }
                ),
                status=403,
                mimetype="application/json",
            )

        # get the location of the user
        required_fields = ["country", "province", "district", "sector"]
        if not all(field in request.json for field in required_fields):
            return Response(
                response=json.dumps(
                    {
                        "status": "bad request",
                        "message": "All location details are required!",
                    }
                ),
                status=400,
                mimetype="application/json",
            )

        # create the location
        location = UserLocations(
            user_id=user["user_id"],
            country=request.json["country"],
            province=request.json["province"],
            district=request.json["district"],
            sector=request.json["sector"],
        )

        db.session.add(location)

        cart = Carts.query.filter_by(owner_id=user["user_id"]).first()
        if not cart:
            return Response(
                response=json.dumps(
                    {
                        "status": "error",
                        "message": "Cart not found for the user!",
                    }
                ),
                status=404,
                mimetype="application/json",
            )
        cart_items = cart.cart_items.all()

        if len(cart_items) == 0:
            return Response(
                response=json.dumps(
                    {"status": "empty cart", "message": "Cart is empty..."}
                ),
                status=200,
                mimetype="application/json",
            )

        # Calculate total price of the order
        total_price = sum(cart_item.total_price for cart_item in cart.cart_items)

        # get the location and create the order
        l = UserLocations.query.filter_by(user_id=user["user_id"]).first()
        order = Orders(
            user_id=user["user_id"],
            location_id=l.id,
            total_price=total_price,
            order_date=datetime.utcnow(),
            status="PENDING",
        )

        db.session.add(order)
        db.session.commit()

        order_items = []
        for cart_item in cart_items:
            order_item = OrderItems(
                order_id=order.id,
                product_name=cart_item.product_name,
                quantity=cart_item.quantity,
                total_price=cart_item.total_price,
            )
            order_items.append(order_item)
            db.session.add(order_item)

        # db.session.commit()

        # clear the cart
        cart.total_quantity = 0
        cart.total_price = 0
        cart.cart_items = []

        db.session.commit()
        order_data = {
            "id": order.id,
            "user_id": order.user_id,
            "total_price": order.total_price,
            "order_date": order.order_date.strftime("%Y-%m-%d %H:%M:%S"),
            "order_items": [
                {
                    "product_name": item.product_name,
                    "quantity": item.quantity,
                    "total_price": item.total_price,
                }
                for item in order_items
            ],
        }
        return Response(
            response=json.dumps(
                {
                    "status": "success",
                    "message": "Order placed successfully!",
                    "order_id": order_data,
                }
            ),
            status=201,
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


@orders.route("/all", methods=["GET"])
@token_required
def getOrders(user):
    try:
        if user["role"] == "CLIENT":
            return Response(
                response=json.dumps(
                    {
                        "status": "forbidden",
                        "message": "You are not allowed to perform this action!",
                    }
                ),
                status=403,
                mimetype="application/json",
            )

        # Fetch all orders with their owner and order items
        orders = Orders.query.all()
        order_list = []

        for order in orders:
            order_items = []
            for item in order.order_items:
                order_item_data = {
                    "product_name": item.product_name,
                    "quantity": item.quantity,
                    "id": item.id,
                    "price": item.total_price,
                }
                order_items.append(order_item_data)

            order_object = {
                "id": order.id,
                "user": {
                    "id": order.user.id,
                    "username": order.user.username,
                    "email": order.user.email,
                },
                "location": {
                    "id": order.location.id,
                    "country": order.location.country,
                    "province": order.location.province,
                    "district": order.location.district,
                    "sector": order.location.sector,
                },
                "total_price": order.total_price,
                "status": order.status,
                "order_items": order_items,
                "order_date": order.order_date.isoformat(),
            }
            order_list.append(order_object)

        if len(order_list) == 0:
            return Response(
                response=json.dumps(
                    {
                        "status": "no orders",
                        "message": "No orders found!",
                    }
                ),
                status=200,
                mimetype="application/json",
            )

        return Response(
            response=json.dumps(
                {
                    "status": "success",
                    "message": "Orders fetched successfully...",
                    "orders": order_list,
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


@orders.route("/mine", methods=["GET"])
@token_required
def getMyOrders(user):
    try:
        if user["role"] != "CLIENT":
            return Response(
                response=json.dumps(
                    {
                        "status": "forbidden",
                        "message": "You are not allowed to perform this action!",
                    }
                ),
                status=403,
                mimetype="application/json",
            )
        # Fetch orders belonging to the user
        orders = Orders.query.filter_by(user_id=user["user_id"]).all()
        order_list = []

        for order in orders:
            order_items = []
            for item in order.order_items:
                order_item_data = {
                    "product_name": item.product_name,
                    "quantity": item.quantity,
                    "id": item.id,
                    "price": item.total_price,
                }
                order_items.append(order_item_data)

            order_object = {
                "id": order.id,
                "user": {
                    "id": order.user.id,
                    "username": order.user.username,
                    "email": order.user.email,
                },
                "location": {
                    "id": order.location.id,
                    "country": order.location.country,
                    "province": order.location.province,
                    "district": order.location.district,
                    "sector": order.location.sector,
                },
                "total_price": order.total_price,
                "status": order.status,
                "order_items": order_items,
                "order_date": order.order_date.isoformat(),
            }
            order_list.append(order_object)

        if len(order_list) == 0:
            return Response(
                response=json.dumps(
                    {
                        "status": "no orders",
                        "message": "No orders found!",
                    }
                ),
                status=200,
                mimetype="application/json",
            )

        return Response(
            response=json.dumps(
                {
                    "status": "success",
                    "message": "Orders fetched successfully...",
                    "orders": order_list,
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


@orders.route("/<int:order_id>")
@token_required
def getOrderById(user, order_id):
    try:
        # Fetch the order by ID
        if user["role"] == "CLIENT":
            order = Orders.query.filter_by(id=order_id, user_id=user["user_id"]).first()
        else:
            order = Orders.query.get(order_id)

        if not order:
            return Response(
                response=json.dumps(
                    {
                        "status": "not found",
                        "message": "Order not found!",
                    }
                ),
                status=404,
                mimetype="application/json",
            )

        order_items = []
        for item in order.order_items:
            order_item_data = {
                "product_name": item.product_name,
                "quantity": item.quantity,
                "id": item.id,
                "price": item.total_price,
            }
            order_items.append(order_item_data)

        order_object = {
            "id": order.id,
            "user": {
                "id": order.user.id,
                "username": order.user.username,
                "email": order.user.email,
            },
            "location": {
                "id": order.location.id,
                "country": order.location.country,
                "province": order.location.province,
                "district": order.location.district,
                "sector": order.location.sector,
            },
            "total_price": order.total_price,
            "status": order.status,
            "order_items": order_items,
            "order_date": order.order_date.isoformat(),
        }

        return Response(
            response=json.dumps(
                {
                    "status": "success",
                    "message": "Order fetched successfully...",
                    "order": order_object,
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


@orders.route("/<int:order_id>/deliver", methods=["PUT"])
@token_required
def deliver(user, order_id):
    try:
        if user["role"] == "CLIENT":
            return Response(
                response=json.dumps(
                    {
                        "status": "forbidden",
                        "message": "You are not allowed to perform this action!",
                    }
                ),
                status=403,
                mimetype="application/json",
            )

        # change the status to delivered and send an email to the owner
        order = Orders.query.filter_by(id=order_id, status="PENDING").first()
        if not order:
            return Response(
                response=json.dumps(
                    {
                        "status": "not found",
                        "message": "Order not found!",
                    }
                ),
                status=404,
                mimetype="application/json",
            )

        # set the status to delivered
        order.status = "DELIVERED"
        name = order.user.username
        country = order.location.country
        province = order.location.province
        district = order.location.district
        sector = order.location.sector
        message = "DELIVERY CONFIRMATION MESSAGE"
        body = f"Hello {name}! Your order is on the way to {country}, {province}, {district}, {sector}."
        recipients = [order.user.email]
        # send the email
        b = sendEmail(message=message, body=body, recipients=recipients)
        if not b:
            return Response(
                response=json.dumps(
                    {
                        "status": "failed",
                        "message": "Error while sending the message",
                    }
                ),
                status=500,
                mimetype="application/json",
            )

        db.session.commit()
        return Response(
            response=json.dumps(
                {
                    "status": "success",
                    "message": "Order delivered and message sent to the client!",
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


@orders.route("/<string:status>/all")
@token_required
def getDeliveredOrders(user, status):
    try:
        if user["role"] == "CLIENT":
            return Response(
                response=json.dumps(
                    {
                        "status": "forbidden",
                        "message": "You are not allowed to perform this action!",
                    }
                ),
                status=403,
                mimetype="application/json",
            )
        # get the orders
        orders = Orders.query.filter_by(status=status.upper()).all()
        order_list = []

        for order in orders:
            order_items = []
            for item in order.order_items:
                order_item_data = {
                    "product_name": item.product_name,
                    "quantity": item.quantity,
                    "id": item.id,
                    "price": item.total_price,
                }
                order_items.append(order_item_data)

            order_object = {
                "id": order.id,
                "user": {
                    "id": order.user.id,
                    "username": order.user.username,
                    "email": order.user.email,
                },
                "location": {
                    "id": order.location.id,
                    "country": order.location.country,
                    "province": order.location.province,
                    "district": order.location.district,
                    "sector": order.location.sector,
                },
                "total_price": order.total_price,
                "status": order.status,
                "order_items": order_items,
                "order_date": order.order_date.isoformat(),
            }
            order_list.append(order_object)

        if len(order_list) == 0:
            return Response(
                response=json.dumps(
                    {
                        "status": "no orders",
                        "message": f"No {status.upper()} orders found!",
                    }
                ),
                status=200,
                mimetype="application/json",
            )

        return Response(
            response=json.dumps(
                {
                    "status": "success",
                    "message": "Orders fetched successfully...",
                    "orders": order_list,
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
