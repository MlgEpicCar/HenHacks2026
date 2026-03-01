from flask import render_template, request, session, redirect, url_for, flash
from models import db, Goal
from accounts import register_user, authenticate_user

def setup_routes(app):
    @app.route("/")
    def index():
        goals = []
        if "user_id" in session:
            goals = Goal.query.filter_by(user_id=session["user_id"]).all()
        return render_template("index.html", goals=goals)

    @app.route("/add_goal", methods=["POST"])
    def add_goal():
        if "user_id" not in session:
            return {"error": "not logged in"}, 401
        data = request.get_json() or {}
        text = data.get("text")
        if not text:
            return {"error": "no text"}, 400
        goal = Goal(text=text, user_id=session["user_id"])
        db.session.add(goal)
        db.session.commit()
        return {"id": goal.id, "text": goal.text, "completed": goal.completed}

    @app.route("/gaming")
    def gaming():
        return render_template("gaming.html")
    
    @app.route("/profile")
    def profile():
        return render_template("profile.html")
    
    @app.route("/settings")
    def settings():
        return render_template("settings.html")
    
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]

            if register_user(username, password):
                return redirect(url_for("login"))
            else:
                return "Username already exists!"

        return render_template("register.html")
    
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]

            user = authenticate_user(username, password)

            if user:
                session["user_id"] = user.id
                return render_template("index.html")
            else:
                return "Invalid login."

        return render_template("login.html")
    
    @app.route("/logout")
    def logout():
        session.pop("user_id", None)
        flash("You have been logged out.")
        return redirect(url_for("index"))