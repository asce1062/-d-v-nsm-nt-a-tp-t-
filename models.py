from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)


class Movie_User_Link_Table(db.Model):
    """Store linking IDs for movies and users."""

    __tablename__ = "movie_user_link"

    id = db.Column(db.Integer, autoincrement=True,
                   primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    movie_id = db.Column(db.Integer, db.ForeignKey("movie.id"))

    movies = db.relationship("Movie")
    users = db.relationship("User")


class Movie(db.Model):
    """Store the Movie details."""
    id = db.Column(db.Integer, autoincrement=True,
                   primary_key=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(120), nullable=False)
    watching = db.Column(db.Boolean, default=False)
    completed = db.Column(db.Boolean, default=False)


class User(db.Model):
    """Store User details."""
    id = db.Column(db.Integer, autoincrement=True,
                   primary_key=True, nullable=False)
    name = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    movies = db.relationship("Movie",
                             secondary="movie_user_link", lazy="dynamic")


# Create the database tables.
db.create_all()
