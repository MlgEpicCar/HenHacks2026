def setup_socket_handlers(socketio):
    from flask import request
    from flask_socketio import emit

    global players, positions

    players = {}
    positions = {
        "player1": {"x": 50, "y": 50},
        "player2": {"x": 300, "y": 50}
    }

    @socketio.on("connect")
    def handle_connect():
        sid = request.sid 
        if "player1" not in players.values():
            players[sid] = "player1"
        elif "player2" not in players.values():
            players[sid] = "player2"
        else:
            players[sid] = None
        emit("init", {"player": players[sid], "positions": positions})

    @socketio.on("move")
    def handle_move(data):
        sid = request.sid
        player = players.get(sid)
        if player not in ["player1","player2"]:
            return

        # Expect data to contain a list of keys, e.g., ["w","d"]
        keys = data.get("key", [])

        # Update positions for each key pressed
        if "w" in keys:
            positions[player]["y"] -= 5
        if "s" in keys:
            positions[player]["y"] += 5
        if "a" in keys:
            positions[player]["x"] -= 5
        if "d" in keys:
            positions[player]["x"] += 5

        # Broadcast updated positions to all clients
        emit("update", positions, to=None)

    @socketio.on("disconnect")
    def handle_disconnect():
        sid = request.sid
        player = players.get(sid)
        if player in ["player1","player2"]:
            positions[player] = {"x":0,"y":0}
        players.pop(sid, None)
        emit("update", positions, to=None)