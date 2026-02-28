from flask import render_template, request, session, redirect, url_for, flash
from accounts import register_user, authenticate_user

def setup_routes(app):
    @app.route("/")
    def index():
        return render_template("index.html")

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