from models import db, User, Goal
from werkzeug.security import generate_password_hash, check_password_hash

# Accounts module reuses the User model defined in models.py
# and the shared SQLAlchemy instance (`db`).
# Password helper methods are added dynamically below.

def _user_set_password(self, password):
    self.password = generate_password_hash(password)


def _user_check_password(self, password):
    return check_password_hash(self.password, password)

def create_default_goals(user):
    default_goals = [
        {"text": "Complete my profile", "priority": 4},
        {"text": "Add my first friend", "priority": 3},
        {"text": "Play my first game", "priority": 3},
        {"text": "Drink enough water", "priority": 2},
    ]

    for g in default_goals:
        goal = Goal(
            user_id=user.id,
            text=g["text"],
            priority=g["priority"],
            completed=False
        )
        db.session.add(goal)

    db.session.commit()

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
    create_default_goals(new_user)
    return True


def authenticate_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user
    return None