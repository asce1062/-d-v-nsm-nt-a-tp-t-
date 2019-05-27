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
        existing_user = User.query.filter_by(
            name=payload.get("username")).first()

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


@app.route("/login", methods=["POST"])
def login():
    """Login existing users."""
    payload = request.get_json(silent=True)

    identity_details = identity(payload)

    if identity_details:
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
                'iat': datetime.datetime.utcnow(),
                'sub': identity_details
            }
            token = jwt.encode(payload, os.environ['SECRET'],
                               algorithm='HS256')
            return response_builder({
                "message": "Login successful.",
                "status": "success",
                "token": str(token)
            }, 200)
        except Exception as e:
            return response_builder({
                "message": "Username and password are incorrect.",
                "status": "fail",
                "error": str(e)
            }, 400)
    else:
        return response_builder({
            "message": "Username and password are incorrect.",
            "status": "fail"
        }, 400)


@app.route("/movie/add", methods=["POST"])
@token_required
def add_movie():
    """Add movie to system."""
    payload = request.get_json(silent=True)

    if not payload:
        return response_builder({
            "message": "Full details have not been provided.",
            "status": "fail"
        }, 400)

    if payload.get('name') and payload.get('description'):
        movie = Movie.query.filter_by(name=payload.get("name")).first()

        if movie:
            return response_builder({
                "message": "Movie already exists.",
                "status": "fail"
            }, 403)
        else:
            new_movie = Movie(
                name=payload.get('name'),
                description=payload.get('description')
            )
            db.session.add(new_movie)
            db.session.commit()
            return response_builder({
                "message": "Movie addition successful.",
                "status": "success"
            })
    else:
        return response_builder({
            "message": "Full details have not been provided.",
            "status": "fail"
        }, 400)
