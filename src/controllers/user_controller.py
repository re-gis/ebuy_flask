from flask import request, Response, Blueprint, json
from src.models.models import Users, Carts
from flask_bcrypt import bcrypt, Bcrypt
from datetime import datetime
from jwt import PyJWT
import os
from src import db
from functools import wraps
from src.middlewares.protected_middleware import token_required


users = Blueprint("users", __name__)
bcrypt = Bcrypt()
jwt = PyJWT()


@users.route("/register", methods=["POST", "GET"])
def registerUser():
    try:
        data = request.json
        if "email" and "password" and "username" in data:
            user = Users.query.filter_by(email=data["email"]).first()
            role = "CLIENT"
            if "role" in data:
                if data["role"] == "SELLER":
                    role = "SELLER"
                else:
                    return Response(
                        response=json.dumps(
                            {"status": "failed", "message": "Use role not supported!"}
                        ),
                        status=400,
                        mimetype="application/json",
                    )

            if not user:
                user_object = Users(
                    username=data["username"],
                    email=data["email"],
                    password=bcrypt.generate_password_hash(data["password"]).decode(
                        "utf-8"
                    ),
                    role=role,
                )
                db.session.add(user_object)
                db.session.commit()

                payload = {
                    "iat": datetime.utcnow(),
                    "user_id": str(user_object.id).replace("-", ""),
                    "username": user_object.username,
                    "email": user_object.email,
                    "role": user_object.role,
                }

                token = jwt.encode(
                    payload=payload, key=os.getenv("SECRET_KEY"), algorithm="HS256"
                )
                
                # create user cart
                cart = Carts(
                    owner_id=user_object.id
                )
                
                db.session.add(cart)
                db.session.commit()
                return Response(
                    response=json.dumps(
                        {
                            "status": "success",
                            "message": "User registered Successfully...",
                            "token": token,
                        }
                    ),
                    status=201,
                    mimetype="application/json",
                )

            else:
                return Response(
                    response=json.dumps(
                        {
                            "status": "failed",
                            "message": "User already exists...",
                        }
                    ),
                    status=409,
                    mimetype="application/json",
                )

        else:
            return Response(
                response=json.dumps(
                    {
                        "status": "failed",
                        "message": "User Parameters Username, Email and Password are required",
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


@users.route("/login", methods=["POST"])
def login():
    try:
        # first check user parameters
        data = request.json
        if "email" and "password" in data:
            # check db for user records
            user = Users.query.filter_by(email=data["email"]).first()

            # if user records exists we will check user password
            if user:
                # check user password
                if bcrypt.check_password_hash(user.password, data["password"]):
                    # user password matched, we will generate token
                    payload = {
                        "iat": datetime.utcnow(),
                        "user_id": str(user.id).replace("-", ""),
                        "username": user.username,
                        "email": user.email,
                        "role": user.role,
                    }
                    token = jwt.encode(
                        payload, os.getenv("SECRET_KEY"), algorithm="HS256"
                    )
                    return Response(
                        response=json.dumps(
                            {
                                "status": "success",
                                "message": "User Sign In Successful",
                                "token": token,
                            }
                        ),
                        status=200,
                        mimetype="application/json",
                    )

                else:
                    return Response(
                        response=json.dumps(
                            {"status": "failed", "message": "User Password Mistmatched"}
                        ),
                        status=401,
                        mimetype="application/json",
                    )
            # if there is no user record
            else:
                return Response(
                    response=json.dumps(
                        {
                            "status": "failed",
                            "message": "User Record doesn't exist, kindly register",
                        }
                    ),
                    status=404,
                    mimetype="application/json",
                )
        else:
            # if request parameters are not correct
            return Response(
                response=json.dumps(
                    {
                        "status": "failed",
                        "message": "User Parameters Email and Password are required",
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


@users.route("/update/<int:id>", methods=["PUT"])
@token_required
def update(user, id):
    try:
        if str(user["user_id"]) != str(id):
            return Response(
                response=json.dumps(
                    {
                        "status": "Not authorised",
                        "message": "You are allowed to update your own account only!",
                    }
                ),
                status=403,
                mimetype="application/json",
            )
        user = Users.query.get(id)
        if not user:
            return Response(
                response=json.dumps(
                    {
                        "status": "Not Found!",
                        "message": "User not found!",
                    }
                ),
                status=404,
                mimetype="application/json",
            )

        data = request.json
        if "username" in data and data["username"] != "":
            user.username = data["username"]

        if "email" in data and data["email"] != "":
            user.email = data["email"]

        if "new_password" in data and data["new_password"] != "":
            user.password = bcrypt.generate_password_hash(data["password"]).decode(
                "utf-8"
            )

        if "password" not in data:
            return Response(
                response=json.dumps(
                    {
                        "status": "invalid",
                        "message": "Provide a password to confirm update!",
                    }
                ),
                status=400,
                mimetype="application/json",
            )

        if not bcrypt.check_password_hash(user.password, data["password"]):
            return Response(
                response=json.dumps(
                    {
                        "status": "invalid",
                        "message": "Invalid password!",
                    }
                ),
                status=400,
                mimetype="application/json",
            )

        db.session.commit()
        payload = {
            "iat": datetime.utcnow(),
            "user_id": str(user.id).replace("-", ""),
            "firstname": user.username,
            "email": user.email,
        }
        token = jwt.encode(payload, os.getenv("SECRET_KEY"), algorithm="HS256")
        user_object = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }
        return Response(
            response=json.dumps(
                {
                    "status": "success",
                    "message": "User updated successfully...",
                    "user": user_object,
                    "token": token,
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


@users.route("/", methods=["GET"])
@token_required
def getUsers(user):
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
        users = Users.query.all()
        u_list = []

        for user in users:
            user_data = {"id": user.id, "username": user.username, "email": user.email}
            u_list.append(user_data)
        if len(u_list) == 0:
            return Response(
                response=json.dumps({"status": "OK", "message": "No users found!"}),
                status=200,
                mimetype="application/json",
            )
        return Response(
            response=json.dumps({"status": "OK", "users": u_list}),
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


@users.route("/delete/<int:id>", methods=["DELETE"])
@token_required
def delete(user, id):
    try:
        if str(user["user_id"]) != str(id):
            return Response(
                response=json.dumps(
                    {
                        "status": "Not authorised",
                        "message": "You are allowed to delete your own account only!",
                    }
                ),
                status=403,
                mimetype="application/json",
            )
        # get the user
        user = Users.query.get(id)
        if not user:
            return Response(
                response=json.dumps(
                    {"status": "Not found!", "message": "User not found!"}
                ),
                status=404,
                mimetype="application/json",
            )
        else:
            data = request.json
            if "password" not in data:
                return Response(
                    response=json.dumps(
                        {
                            "status": "Forbidden!",
                            "message": "Password required to delete the user account!",
                        }
                    ),
                    status=404,
                    mimetype="application/json",
                )
            if not bcrypt.check_password_hash(user.password, data["password"]):
                return Response(
                    response=json.dumps(
                        {
                            "status": "Invalid!",
                            "message": "Incorrect password!",
                        }
                    ),
                    status=400,
                    mimetype="application/json",
                )
            db.session.delete(user)
            db.session.commit()
            return Response(
                response=json.dumps(
                    {"status": "success", "message": "User deleted successfully..."}
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
