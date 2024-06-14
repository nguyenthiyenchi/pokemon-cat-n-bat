from flask import Flask, json, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from pokebat.player import Player 
from pokebat.pokebat import PokeBat
import json

app = Flask(__name__)

@app.route('/hello', methods=['POST'])
def hello_handler():
    if request.method != 'POST':
        return jsonify({'error': 'Invalid request method'}), 405

    name = request.form.get('name')
    if not name:
        return jsonify({'error': 'Error parsing form data'}), 400

    print("Received data:", name)
    return f"Hello, {name}!", 200

app = Flask(__name__)

# Global variables to track readiness and players
players = {"u1": None, "u2": None}
ready_status = {"u1": False, "u2": False}
battle = None

@app.route('/')
def index():
    return render_template('pokebat.html')

@app.route('/get_pokemon_list/<username>', methods=['GET'])
def get_pokemon_list(username):
    try:
        with open(f'{username}.json', 'r') as file:
            pokemons = json.load(file)
        return jsonify(pokemons)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ready', methods=['POST'])
def ready():
    data = request.json
    username = data['username']
    selected_pokemons = data['selectedPokemons']
    
    with open(f'u1.json', 'r') as file:
        pokemons = json.load(file)
    
    chosen_pokemons = [p for p in pokemons if p['name'] in selected_pokemons]
    players[username] = Player(username, chosen_pokemons)
    ready_status[username] = True

    if all(ready_status.values()):
        global battle
        battle = PokeBat(players['u1'], players['u2'])
        return jsonify({"status": "ready"})
    else:
        return jsonify({"status": "waiting_for_opponent"})

# @app.route('/battle', methods=['POST'])
# def battle():
#     data = request.json
#     action = data['action']
#     username = data['username']
    
#     if action == "attack":
#         logs = battle.execute_turn()
#         return jsonify({"result": "continue", "logs": logs})
#     elif action == "switch":
#         new_index = data['new_index']
#         player = players[username]
#         player.switch_pokemon(new_index)
#         logs = battle.battle.battle_log
#         return jsonify({"result": "continue", "logs": logs})
#     elif action == "surrender":
#         winner = 'u1' if username == 'u2' else 'u2'
#         logs = [f"{username} surrendered! {winner} wins the battle."]
#         return jsonify({"result": "end", "logs": logs, "winner": winner})

# if __name__ == '__main__':
#     app.run(debug=True)

if __name__ == '__main__':
    app.run(port=8080)
