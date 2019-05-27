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


@token_required
@app.route("/user/link/movie", methods=["POST"])
def link_movie_user():
    """Link movie to user watching it."""
    payload = request.get_json(silent=True)

    if not payload:
        return response_builder({
            "message": "Full details have not been provided.",
            "status": "fail"
        }, 400)

    if payload.get('name'):
        movie = Movie.query.filter_by(name=payload.get("name")).first()

        if not movie:
            return response_builder({
                "message": "Movie doesn't exist. Please add it.",
                "status": "fail"
            }, 403)

        user_id = decode_auth_token(request.headers.get('Authorization'))
        user = User.query.filter_by(id=user_id).first()

        linked_movies = Movie_User_Link_Table.query.filter_by(
            movie_id=movie.id).all()
        for movie in linked_movies:
            if movie.user_id == user.id:
                return response_builder({
                    "message": "Movie has already been linked to user.",
                    "status": "fail"
                }, 403)

        movie_user_link = Movie_User_Link_Table(
            movie_id=movie.id,
            user_id=user.id
        )
        user.movies.append(movie)
        db.session.add(movie_user_link)
        db.session.commit()
        return response_builder({
            "message": "Link of {} to User {} successful.".format(movie.name,
                                                                  user.name),
            "status": "success"
        })

    else:
        return response_builder({
            "message": "Movie name must be provided.",
            "status": "fail"
        }, 403)


@token_required
@app.route("/user/movies", methods=["GET"])
def view_linked_movies():
    """View movies linked to logged in user."""
    payload = request.get_json(silent=True)

    user_id = decode_auth_token(request.headers.get('Authorization'))
    user = User.query.filter_by(id=user_id).first()

    if len([q for q in user.movies]) == 0:
        return response_builder({
            "message": "User has no movies linked",
            "status": "success"
        }, 200)

    list_movies = []
    watched_movies = []
    for movie in user.movies:
        list_movies.append({
            "movie_name": movie.name,
            "movie_description": movie.description
        })
        if movie.completed:
            watched_movies.append({
                "movie_name": movie.name,
                "movie_description": movie.description
            })

    return response_builder({
        "movies": list_movies,
        "watched_movies": watched_movies,
        "status": "success"
    }, 200)


@token_required
@app.route("/user/movies/update", methods=["PUT"])
def update_completed_movies():
    """Update movies linked to user if completed or not."""
    payload = request.get_json(silent=True)

    if not payload:
        return response_builder({
            "message": "Full details have not been provided.",
            "status": "fail"
        }, 400)

    if payload.get("name"):
        movie = Movie.query.filter_by(name=payload.get("name")).first()

        if not movie:
            return response_builder({
                "message": "Movie doesn't exist. Please register it.",
                "status": "fail"
            }, 403)

        if movie.completed:
            return response_builder({
                "message": "Movie {} already marked as completed.".format(movie.name),
                "status": "fail"
            }, 403)

        user_id = decode_auth_token(request.headers.get('Authorization'))
        user = User.query.filter_by(id=user_id).first()

        linked_movies = Movie_User_Link_Table.query.filter_by(
            movie_id=movie.id).all()
        for update_movie in linked_movies:
            if update_movie.user_id == user.id:
                update_movie_status = Movie.query.filter_by(
                    name=payload.get("name")).first()
                update_movie_status.completed = True
                db.session.commit()

        return response_builder({
            "message": "Movie {} has been marked as completed.".format(movie.name),
            "status": "success"
        }, 200)

    else:
        return response_builder({
            "message": "Name of completed movie must be provided.",
            "status": "fail"
        }, 403)
