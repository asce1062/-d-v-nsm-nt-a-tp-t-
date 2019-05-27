"""Holds all helper functions within the application."""
import bcrypt
import base64
import jwt
import os
from flask import jsonify, request
from functools import wraps
from models import User


def response_builder(data, status_code=200):
    """Build the jsonified response to return."""
    response = jsonify(data)
    response.status_code = status_code
    return response


def identity(payload):
    """
    Returns user info.

    Based of whether it is a login or registration attempt.
    """
    user = User.query.filter_by(name=payload.get('username')).first()

    if user:
        success = bcrypt.checkpw(payload.get('password').encode('utf-8'),
                                 user.password)
        if success:
            return user.id
        else:
            return response_builder({
                "message": "Username and password are incorrect.",
                "status": "fail"
            }, 400)
    else:
        password = bcrypt.hashpw(payload.get('password').encode('utf-8'),
                                 bcrypt.gensalt())
        return payload.get('username'), password, False


def decode_auth_token(auth_token):
    """Decodes the auth token."""
    payload = jwt.decode(auth_token, os.environ['SECRET'])
    return payload['sub']


def token_required(f):
    """Authenticate that a valid Token is present."""
    @wraps(f)
    def decorated(*args, **kwargs):
        authorization_token = request.headers.get('Authorization')
        if not authorization_token:
            return response_builder({
                "message": "Bad request. Header does not contain authorization token"
            }, 400)

        try:
            payload = decode_auth_token(authorization_token)
        except jwt.exceptions.ExpiredSignatureError:
            return response_builder({
                "message": 'Signature expired. Please log in again.',
            }, 401)
        except jwt.exceptions.DecodeError:
            return response_builder({
                "message": 'Invalid token. Please log in again.',
            }, 401)

        return f(*args, **kwargs)
    return decorated
