from flask_sqlalchemy import SQLAlchemy
from models import db
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False) # plain text passwords // hash the passwords if you are planning on releasing this
    xp = db.Column(db.Integer, default=0)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


# -------------------------
# Account Functions
# -------------------------

def register_user(username, password):
    if User.query.filter_by(username=username).first():
        return False  # username taken

    new_user = User(username=username)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()
    return True


def authenticate_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user
    return None