from flask import Flask, session
from flask_socketio import SocketIO

from routes import setup_routes
from easter_egg import setup_socket_handlers
from models import db, User, Goal
# accounts module still provides authentication helpers
from accounts import register_user, authenticate_user

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet") # Allow connections from Ngrok URL

db.init_app(app)

#setups
setup_routes(app)
setup_socket_handlers(socketio)

@app.context_processor
def inject_user():
    if "user_id" in session:
        user = User.query.get(session["user_id"])
        return dict(current_user=user)
    return dict(current_user=None)

with app.app_context():
    db.create_all()  # Creates all tables defined in models.py

if __name__ == "__main__":
    app.run(debug=True)

# if __name__ == "__main__":
    #socketio.run(app, debug=True, host="0.0.0.0", port=5000)