from flask import Flask, render_template, request, redirect
from models import db, User, Goal

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

db.init_app(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    goals = Goal.query.all()
    return render_template("dashboard.html", goals=goals)

if __name__ == "__main__":
    app.run(debug=True)