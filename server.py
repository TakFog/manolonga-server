from flask import Flask, request, jsonify
from collections import defaultdict
import threading
import json
import time
import random
import os

app = Flask(__name__)
states = defaultdict(lambda: defaultdict(dict))
layouts = {}  # Store generated layouts
lock = threading.Lock()
last_updated = {}

# Load configurations from environment variables
PORT = int(os.getenv("SERVER_PORT", 8080))
HOST = os.getenv("SERVER_HOST", "0.0.0.0")
GAME_ID_LENGTH = int(os.getenv("GAME_ID_LENGTH", 4))
DEBUG = os.getenv("DEBUG", 0) == "1"

# Allowed characters for game ID generation
ALLOWED_CHARS = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"

def generate_game_id():
    return ''.join(random.choices(ALLOWED_CHARS, k=GAME_ID_LENGTH))

def deterministic_random(seed, min_val, max_val, count):
    rnd = random.Random(seed)
    return sorted(rnd.sample(range(min_val, max_val), count))

def generate_random_values(rnd, min_val, max_val, count):
    return sorted(rnd.sample(range(min_val, max_val), count))

@app.route("/createGame")
def create_game():
    with lock:
        while True:
            gameid = generate_game_id()
            if gameid not in states:
                states[gameid] = defaultdict(dict)
                last_updated[gameid] = time.time()
                app.logger.info(f"Created new game with ID {gameid}")
                return jsonify({"gameid": gameid})

@app.route("/<string:gameid>/init", methods=["POST"])
def generate_layout(gameid):
    with lock:
        if gameid in layouts:
            return jsonify(layouts[gameid])
        
        data = request.get_json()
        num_exits = data.get("numExits")
        num_open_exits = data.get("numOpenExits")
        num_monster_spawns = data.get("numMonsterSpawns")
        num_child_spawns = data.get("numChildSpawns")
        
        rnd = random.Random(time.time())
        open_exits = generate_random_values(rnd, 0, num_exits, num_open_exits)
        monster_spawn = generate_random_values(rnd, 0, num_monster_spawns, 1)[0]
        child_spawn = generate_random_values(rnd, 0, num_child_spawns, 1)[0]
        
        layout = {
            "openExits": open_exits,
            "monsterSpawn": monster_spawn,
            "childSpawn": child_spawn
        }
        layouts[gameid] = layout
        return jsonify(layout)
      

@app.route("/<string:gameid>/updateState/<string:player_id>/<int:round_id>", methods=["POST"])
def update_state(gameid, player_id, round_id):
    with lock:
        state_payload = request.get_json()
        round_state = states[gameid].setdefault(round_id, {})
        
        if player_id in round_state and isinstance(round_state[player_id], dict) and isinstance(state_payload, dict):
            round_state[player_id].update(state_payload)
        else:
            round_state[player_id] = state_payload
        
        if player_id.lower() == "monster":
            round_state["hasMonster"] = True
        else:
            round_state["hasChild"] = True
        
        states[gameid].pop(round_id - 2, None)  # Clean up old states
        last_updated[gameid] = time.time()
        
        app.logger.info(f"State updated for player {player_id} in round {round_id} of game {gameid}: {json.dumps(states)}")
        return jsonify(round_state)

@app.route("/<string:gameid>/clear", methods=["GET"])
def clear(gameid):
    with lock:
        if states[gameid]:
            max_round = max(states[gameid].keys(), default=0)
            if max_round > 0:
                layouts.pop(gameid, None)
                last_updated.pop(gameid, None)
            states.pop(gameid, None)
            app.logger.info(f"State cleared for game {gameid}")
    return "State cleared", 200

def cleanup_old_games():
    while True:
        time.sleep(3600)  # Run every hour
        current_time = time.time()
        with lock:
            for gameid in list(last_updated.keys()):
                if current_time - last_updated[gameid] > 86400:  # 24 hours
                    app.logger.info(f"Deleting stale game {gameid}")
                    states.pop(gameid, None)
                    layouts.pop(gameid, None)
                    last_updated.pop(gameid, None)

# Start background cleanup thread
cleanup_thread = threading.Thread(target=cleanup_old_games, daemon=True)
cleanup_thread.start()

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG)
