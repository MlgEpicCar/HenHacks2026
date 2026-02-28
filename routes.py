from flask import render_template

def setup_routes(app):
    @app.route("/login")
    def login():
        return render_template("login.html")
    
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/gaming")
    def gaming():
        return render_template("gaming.html")
    
    @app.route("/profile")
    def profile():
        return render_template("profile.html")