from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

friendships = db.Table(
    'friendships',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('friend_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

# -----------------------------
#           MODELS
# -----------------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    level = db.Column(db.Integer, default=1)
    xp = db.Column(db.Integer, default=0)
    pfp = db.Column(db.String, default="unknown")
    bio = db.Column(db.String(250), default="Enter bio here.")

    # Link to friends
    friends = db.relationship(
        'User',
        secondary=friendships,
        primaryjoin=id==friendships.c.user_id,
        secondaryjoin=id==friendships.c.friend_id,
        backref='friend_of'
    )

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200))
    completed = db.Column(db.Boolean, default=False)
    priority = db.Column(db.Integer, default=3)
    user_id = db.Column(db.Integer)

class FriendRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    from_user = db.relationship("User", foreign_keys=[from_user_id])
    to_user = db.relationship("User", foreign_keys=[to_user_id])

class RPSGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player1_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    player2_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    player1_choice = db.Column(db.String(10), default=None)
    player2_choice = db.Column(db.String(10), default=None)
    winner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    player1 = db.relationship("User", foreign_keys=[player1_id])
    player2 = db.relationship("User", foreign_keys=[player2_id])
    winner = db.relationship("User", foreign_keys=[winner_id])

class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    game_type = db.Column(db.String(50), nullable=False)  # e.g., "rps"
    status = db.Column(db.String(20), default="pending")   # "pending", "accepted", "started", "denied"
    game_id = db.Column(db.Integer, nullable=True)

    from_user = db.relationship("User", foreign_keys=[from_user_id], backref="sent_challenges")
    to_user = db.relationship("User", foreign_keys=[to_user_id], backref="received_challenges")