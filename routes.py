from flask import render_template

def setup_routes(app):
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/gaming")
    def gaming():
        return render_template("gaming.html")