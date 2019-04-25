import jwt
import os
import datetime
from flask import request
from models import app, User, Movie, Movie_User_Link_Table, db
from auth_helpers import (response_builder, identity, decode_auth_token,
                     token_required)

@app.route("/")
def hello():
    """Home Page."""
    return "Welcome to the Movie Tracker"


@app.route("/register", methods=["POST"])
def register():
    """Register a new User in the application."""
    payload = request.get_json(silent=True)

    if not payload:
        return response_builder({
            "message": "Full credentials have not been provided.",
            "status": "fail"
            }, 400)

    if payload.get('username') and payload.get('password'):
        identity_details = identity(payload)
        existing_user = User.query.filter_by(name=payload.get("username")).first()

        if existing_user:
            return response_builder({
                "message": "User already exists. Please login.",
                "status": "fail"
                }, 403)
        else:
            new_user = User(
                name=identity_details[0],
                password=identity_details[1]
            )
            db.session.add(new_user)
            db.session.commit()
            return response_builder({
                "message": "User registration successful.",
                "user_id": str(new_user.id),
                "status": "success"
                })
    else:
        return response_builder({
            "message": "Full credentials have not been provided.",
            "status": "fail"
            }, 400)