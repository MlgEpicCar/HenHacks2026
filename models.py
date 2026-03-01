from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    xp = db.Column(db.Integer, default=0)
    pfp = db.Column(db.String, default="unknown")
    bio = db.Column(db.String(250), default="This user hasn't set a bio yet.")

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200))
    completed = db.Column(db.Boolean, default=False)
    priority = db.Column(db.Integer, default=3)  # 1-5 scale
    user_id = db.Column(db.Integer)