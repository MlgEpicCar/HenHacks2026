from flask import render_template, request, session, redirect, url_for, flash, jsonify
from models import db, Goal
from accounts import register_user, authenticate_user, User

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
        priority = data.get("priority", 3)
        if not text:
            return {"error": "no text"}, 400
        goal = Goal(text=text, user_id=session["user_id"], priority=priority)
        db.session.add(goal)
        db.session.commit()
        return {"id": goal.id, "text": goal.text, "completed": goal.completed, "priority": goal.priority}

    @app.route("/delete_goal", methods=["POST"])
    def delete_goal():
        if "user_id" not in session:
            return jsonify(error="not logged in"), 401
        data = request.get_json() or {}
        goal_id = data.get("id")
        if not goal_id:
            return jsonify(error="no id"), 400
        goal = Goal.query.get(goal_id)
        if not goal or goal.user_id != session.get("user_id"):
            return jsonify(error="not found"), 404
        db.session.delete(goal)
        db.session.commit()
        return jsonify(success=True)

    @app.route("/toggle_goal", methods=["POST"])
    def toggle_goal():
        if "user_id" not in session:
            return jsonify(error="not logged in"), 401
        data = request.get_json() or {}
        goal_id = data.get("id")
        completed = data.get("completed")
        if goal_id is None or completed is None:
            return jsonify(error="missing fields"), 400
        goal = Goal.query.get(goal_id)
        if not goal or goal.user_id != session.get("user_id"):
            return jsonify(error="not found"), 404
        # only award xp when marking completed true from false
        xp_awarded = 0
        if completed and not goal.completed:
            xp_awarded = goal.priority or 1
            user = User.query.get(session["user_id"])
            user.xp = (user.xp or 0) + xp_awarded
            db.session.add(user)
        goal.completed = bool(completed)
        db.session.add(goal)
        db.session.commit()
        return jsonify(success=True, xp= xp_awarded)

    @app.route("/gaming")
    def gaming():
        return render_template("gaming.html")
    
    @app.route("/profile", methods=["GET", "POST"])
    def profile():
        user = User.query.get(session.get("user_id"))

        if request.method == "POST":
            user.bio = request.form["bio"]
            user.pfp = request.form["pfp"]

            db.session.commit()
            return redirect(url_for("profile"))

        return render_template("profile.html", user=user)
    
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