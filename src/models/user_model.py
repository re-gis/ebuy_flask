from flask_sqlalchemy import SQLAlchemy
from src import db

class Users(db.Model):
    __table__name = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=True)

    def __str__(self):
        return self.email
