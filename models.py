from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


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
    completed = db.Column(db.Boolean, default=False)


class User(db.Model):
    """Store User details."""
    id = db.Column(db.Integer, autoincrement=True,
                   primary_key=True, nullable=False)
    name = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    movies = db.relationship("Movie",
                             secondary="movie_user_link", lazy="dynamic")

if __name__ == '__main__':
    manager.run()
