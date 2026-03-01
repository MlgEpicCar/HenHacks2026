from flask import render_template, request, session, redirect, url_for, flash, jsonify
from models import db, Goal, FriendRequest
from accounts import register_user, authenticate_user, User

def get_current_user():
    """Return the logged-in user object based on session['user_id']."""
    user_id = session.get("user_id")  # session must store the logged-in user's ID
    if not user_id:
        return None
    return User.query.get(user_id)

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
            # recalc level based on 10 xp per level
            user.level = (user.xp // 10) if user.xp is not None else 0
            db.session.add(user)
        goal.completed = bool(completed)
        db.session.add(goal)
        db.session.commit()
        return jsonify(success=True, xp=xp_awarded)

    @app.route("/playground")
    def playground():
        return render_template("playground.html")
    
    @app.route("/profile", methods=["GET", "POST"])
    def profile():
        user = User.query.get(session.get("user_id"))
        pending_requests = FriendRequest.query.filter_by(to_user_id=user.id).all()

        if request.method == "POST":
            user.bio = request.form["bio"]
            user.pfp = request.form["pfp"]

            db.session.commit()
            return redirect(url_for("profile"))

        return render_template("profile.html", user=user, pending_requests=pending_requests)
    
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
    
    @app.route("/add_friend_by_name", methods=["POST"])
    def add_friend_by_name():
        current_user = get_current_user()
        if not current_user:
            flash("You must be logged in to add friends.", "error")
            return redirect(url_for("login"))

        username = request.form.get("username", "").strip()
        if not username:
            flash("Please enter a username.", "error")
            return redirect(url_for("profile"))

        friend = User.query.filter_by(username=username).first()
        if not friend:
            flash(f"User '{username}' not found.", "error")
            return redirect(url_for("profile"))

        if friend.id == current_user.id:
            flash("You can't friend yourself.", "error")
            return redirect(url_for("profile"))

        # Check if already friends
        if friend in current_user.friends:
            flash(f"{friend.username} is already your friend.", "info")
            return redirect(url_for("profile"))

        # Check if a pending request already exists
        existing_request = FriendRequest.query.filter_by(from_user_id=current_user.id, to_user_id=friend.id).first()
        if existing_request:
            flash(f"Friend request to {friend.username} is already pending.", "info")
            return redirect(url_for("profile"))

        # Create a new friend request
        new_request = FriendRequest(from_user_id=current_user.id, to_user_id=friend.id)
        db.session.add(new_request)
        db.session.commit()
        flash(f"Friend request sent to {friend.username}!", "success")
        return redirect(url_for("profile"))
    
    @app.route("/respond_friend_request/<int:request_id>", methods=["POST"])
    def respond_friend_request(request_id):
        current_user = get_current_user()
        if not current_user:
            flash("You must be logged in.", "error")
            return redirect(url_for("login"))

        fr = FriendRequest.query.get(request_id)
        if not fr or fr.to_user_id != current_user.id:
            flash("Invalid request.", "error")
            return redirect(url_for("profile"))

        action = request.form.get("action")
        if action == "accept":
            # Make them mutual friends
            current_user.friends.append(fr.from_user)
            fr.from_user.friends.append(current_user)
            flash(f"You are now friends with {fr.from_user.username}!", "success")
        else:
            flash(f"Friend request from {fr.from_user.username} denied.", "info")

        db.session.delete(fr)
        db.session.commit()
        return redirect(url_for("profile"))
    
    @app.route("/remove_friend/<int:friend_id>", methods=["POST"])
    def remove_friend(friend_id):
        current_user = get_current_user()
        if not current_user:
            flash("You must be logged in to remove friends.", "error")
            return redirect(url_for("login"))

        friend = User.query.get(friend_id)
        if not friend or friend not in current_user.friends:
            flash("Friend not found.", "error")
            return redirect(url_for("profile"))

        # Remove mutual friendship
        current_user.friends.remove(friend)
        if current_user in friend.friends:
            friend.friends.remove(current_user)
        db.session.commit()
        flash(f"{friend.username} has been removed from your friends.", "success")
        return redirect(url_for("profile"))