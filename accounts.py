from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

# Accounts module reuses the User model defined in models.py
# and the shared SQLAlchemy instance (`db`).
# Password helper methods are added dynamically below.

def _user_set_password(self, password):
    self.password = generate_password_hash(password)


def _user_check_password(self, password):
    return check_password_hash(self.password, password)

User.set_password = _user_set_password
User.check_password = _user_check_password


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