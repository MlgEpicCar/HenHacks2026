def setup_socket_handlers(socketio):
    from flask import request, url_for, session
    from flask_socketio import emit
    from models import User

    global players, positions

    players = {}
    positions = {
        "player1": {"x": 50, "yOffset": 100},
        "player2": {"x": 300, "yOffset": 100}
    }
    player_users = {}
    usernames = {}

    @socketio.on("connect")
    def handle_connect():
        sid = request.sid

        if "player1" not in players.values():
            players[sid] = "player1"
            player_users["player1"] = session.get("user_id")  # store user id
        elif "player2" not in players.values():
            players[sid] = "player2"
            player_users["player2"] = session.get("user_id")
        else:
            players[sid] = None

        # Prepare PFPs for each assigned player
        pfps = {}
        for player, user_id in player_users.items():
            user = User.query.get(user_id)
            usernames[player] = user.username if user else "Unknown"
            pfps[player] = url_for("static", filename=f"pfps/{user.pfp}.png") if user else ""

        emit("init", {"player": players[sid], "positions": positions, "pfps": pfps, "usernames": usernames})

    @socketio.on("move")
    def handle_move(data):
        sid = request.sid
        player = players.get(sid)
        if player not in ["player1","player2"]:
            return

        # Expect data to contain a list of keys, e.g., ["w","d"]
        keys = data.get("key", [])

        # Left/right movement
        if "a" in keys:
            positions[player]["x"] -= 5
        if "d" in keys:
            positions[player]["x"] += 5

        # Broadcast updated positions to all clients (sometimes lol)
        emit("update", positions, to=None)

    @socketio.on("disconnect")
    def handle_disconnect():
        sid = request.sid
        player = players.get(sid)
        if player in ["player1","player2"]:
            positions[player] = {"x":0,"yOffset": 100}
        players.pop(sid, None)
        emit("update", positions, to=None)