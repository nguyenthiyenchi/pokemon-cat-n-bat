import random, time, json, hashlib, os
from flask import Flask, json, redirect, render_template, request, session, jsonify, url_for
from flask_socketio import SocketIO, disconnect, emit
from pokebat.player import Player 
from pokebat.pokebat import PokeBat
from pokebat.pokemon import Pokemon
from functools import wraps
from datetime import datetime
from threading import Timer

app = Flask("Pokemon-Cat-n-Bat")
app.secret_key = '8hp507'
socketio = SocketIO(app)

# ------------------ POKEMON CATCHING ---------------------

PIN = "netcentriclab"  
PLAYERS_FILE = 'players.json'
PLAYERS_POKEMON_FOLDER = 'players_pokemon'

# Store spawned Pokemon data
spawned_pokemon = []

# Store joined players data
joined_player = []

# Load clients from file JSON
def load_players():
    try:
        with open(PLAYERS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    
# Save clients to file JSON
def save_players(player):
    with open(PLAYERS_FILE, 'w') as f:
        json.dump(player, f, indent=4)

players = load_players()

# Flag to indicate if session should be cleared
app.config['CLEAR_SESSION'] = True

def verify_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'verified' not in session:
            return redirect(url_for('verify'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        pin = request.form['pin']
        if pin == PIN:
            session['verified'] = True
            return redirect(url_for('home'))
    return render_template('verify.html')

@app.route('/')
def root():
    if 'verified' in session:
        return redirect(url_for('home'))  # Redirect verified users to home
    else:
        return redirect(url_for('verify'))
    
# Check if client has used the same pass+name and validate PIN if provided
@app.route('/check_unique', methods=['POST'])
def check_unique():
    data = request.get_json()
    name = data['name']
    password = data['password']
    pin = data.get('pin', '')
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    for player in players:
        if player['name'] == name:
            if player['password'] == hashed_password:
                if pin and pin == player.get('pin'):
                    return jsonify({'unique': True, 'existing': True})
                else:
                    return jsonify({'unique': False})
            else:
                return jsonify({'unique': False})
    return jsonify({'unique': True, 'existing': False})

# Handle client connection
@socketio.on('client_connected')
def handle_client_connected(data):
    name = data['name']
    password = data['password']
    color = data['color']
    pin = data.get('pin', '')
    ip_address = request.remote_addr
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    date_of_submission = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Check if the client is reconnecting with existing credentials
    for player in players:
        if player['name'] == name and player['password'] == hashed_password:
            if pin == player['pin']:
                player_info = player
                break
    else:
        # Generate a new PIN for new clients
        pin = str(random.randint(100000, 999999))
        player_info = {'name': name, 'ip': ip_address, 'password': hashed_password, 'color': color, 'pin': pin, 'date_of_submission': date_of_submission}
        players.append(player_info)
        save_players(players)
        # Create a namePIN.json file in players_pokemon folder
        os.makedirs(PLAYERS_POKEMON_FOLDER, exist_ok=True)
        namePIN_file_path = os.path.join(PLAYERS_POKEMON_FOLDER, f"{name}_{pin}.json")
        with open(namePIN_file_path, 'w') as f:
            json.dump([], f, indent=4)
    
    emit('new_client', player_info, broadcast=True)
    emit('client_pin', {'pin': pin})

@app.route('/server')
@verify_required
def home():
    return render_template('server.html', players=players)

@app.route('/client', methods=['GET'])
def client_page():
    return render_template('client.html')
# ----------- POKEMON --------------

@app.route('/spawn_pokemon', methods=['POST'])
def spawn_pokemon():
    global spawned_pokemon
    data = request.get_json()
    spawned_pokemon.append(data)
    save_pokemon_data()
    return jsonify({'status': 'success'})

@app.route('/despawn_pokemon', methods=['POST'])
def despawn_pokemon():
    global spawned_pokemon
    data = request.get_json()
    # Find and remove the pokemon from spawned_pokemon
    for i, pokemon in enumerate(spawned_pokemon):
        if pokemon['position'] == data['position']:
            del spawned_pokemon[i]
            break
    save_pokemon_data()
    return jsonify({'status': 'success'})

@app.route('/pokemon_data', methods=['GET'])
def get_pokemon_data():
    return jsonify(spawned_pokemon)

def save_pokemon_data():
    with open('pokemon_data.json', 'w') as f:
        json.dump(spawned_pokemon, f)
        
@app.route('/capture', methods=['POST'])
def capture():
    data = request.get_json()
    captured_pokemons.append(data)
    global pokemons
    pokemons = [p for p in pokemons if not (p['x'] == data['x'] and p['y'] == data['y'])]
    return jsonify({"status": "success", "data": data})

# ----------- PLAYER --------------

@app.route('/place_player', methods=['POST'])
def place_player():
    global joined_player
    data = request.get_json()
    joined_player.append(data)
    save_player_data()
    return jsonify({'status': 'success'})

@app.route('/player_data', methods=['GET'])
def get_player_data():
    # Read data from player_data.json file
    with open('player_data.json', 'r') as f:
        player_data = json.load(f)

    # Transform the data to match the client-side expectation
    transformed_data = []
    for player in player_data:
        transformed_data.append({
            'x': player['position']['x'],
            'y': player['position']['y'],
            'color': player['color'],
            'name': player['name']
        })

    return jsonify(transformed_data)

def save_player_data():
    with open('player_data.json', 'w') as f:
        json.dump(joined_player, f)

# ----------- CLEAR --------------

def update_json_file():
    # This function is called every second to update the JSON file
    save_pokemon_data()
    # Schedule the next update
    Timer(1, update_json_file).start()

def clear_json_file():
    # Clear the pokemon_data.json file
    with open('pokemon_data.json', 'w') as f:
        json.dump([], f)  # Write an empty list to the file
        
        
    # Clear the player_data.json file
    with open('player_data.json', 'w') as f:
        json.dump([], f)  # Write an empty list to the file

# ----------------------------------------------------------------

# Constraint of 2 players
MAX_USERS = 2
connected_clients = {}
confirmation = 0
users = []
current_turn = None

@socketio.on('connect')
def handle_connect():
    if len(connected_clients) >= MAX_USERS and confirmation < 2:
        print(f"Server full. Disconnecting client {request.sid}")
        disconnect()
    else:
        client_id = request.sid
        connected_clients[client_id] = request.namespace
        print(f"Client connected: {client_id}")
        
# Establish connection to 2 players in the battle interface
@socketio.on('connect_battle')
def handle_battle_connect(username):
    global current_turn
    client_id = request.sid
    request_user = None
    for user in users:
        if user.name == username: 
            request_user = user  

    for user in users:
        # Get the opponent
        if user.name != username:   
        # Pick player for the first turn
            #The other player's default pokemon has higher speed
            #This version hasn't handle default pokemon have similar speed
            if int(user.pokemon_list[0].speed) >= int(request_user.pokemon_list[0].speed):
                current_turn = user.name
                # print("send not_turn")
                # emit('not_turn')
            else:
                current_turn = request_user.name
                # print("send turn")
                # emit('take_turn')
            emit('turn_change', {'current_turn': current_turn}, broadcast=True)
    
    print(f"Client connected to Battle: {client_id}")

@socketio.on('get_players_name')
def handle_battle_connect(data):
    playername = data.get('username')
    opponentname = ""
    for u in users:
        if u.name != playername:
            opponentname = u.name
    emit('return_players_name',  {'opponentName': opponentname})


@app.route('/ready', methods=['POST'])
def handle_message():
    global confirmation
    global current_turn
    global connected_clients
    if request.method != 'POST':
        return jsonify({'error': 'Invalid request method'}), 405
 
    data = request.get_json()
    if data is None:
        print("Data is null")
        return jsonify({'error': 'Invalid request data'}), 400
    
    username = data.get('username')
    selectedPokemons = data.get('selectedPokemons')
    playerId = data.get('player_id')

    if username is None or selectedPokemons is None:
        print('Missing username or selectedPokemons')
        return jsonify({'error': 'Missing username or selectedPokemons'}), 400
    else:
        confirmation += 1
        print(selectedPokemons)
        print("Receive data from user " + username)

        user = Player(username)
        user.set_id(playerId)
        user.load_pokemons_from_json(username+'.json', selectedPokemons)
        # for poke in user.pokemon_list:
        #     poke.print_info()
        users.append(user)

    print(connected_clients)

    if (confirmation == 2):
        print("Both user confirmed")
        emit('battle_ready', {'message': 'Both_Ready'}, broadcast=True, namespace='/')
        connected_clients = {}
        print ("After confirmed: ")
        print (connected_clients)

        return jsonify({'status': 'success', 'redirect': url_for('battle')}), 200
    return jsonify({'status': 'success'}), 200



@app.route('/ready')
def ready():
    return render_template('pokebat_ready.html')


@app.route('/battle')
def battle():
    if (confirmation == 2):
        return render_template('pokebat_battle.html')
    return jsonify({'error': 'Both users are not ready yet'}), 400


@app.route('/get_pokemon_list/<username>', methods=['GET'])
def get_pokemon_list(username):
    try:
        with open(f'{username}.json', 'r') as file:
            pokemons = json.load(file)
        return jsonify(pokemons)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Use this route to handle the turn 
@app.route('/get_battle_pokemon_list/<username>', methods=['GET'])
def get_battle_pokemon_list(username):
    print("Username: " + username)
    try:
        for user in users:
            print("check1")
            print("user.id: " + str(user.name) + " userId: " + str(username))
            if user.name == username:
                print("check2")
                print(user.get_pokemons_as_json())
                return jsonify(user.get_pokemons_as_json())
                
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return []
    
@app.route('/get_battle_opponent_pokemon_list/<username>', methods=['GET'])
def get_battle_opponent_pokemon_list(username):
    print("Username: " + username)

    try:
        for user in users:
            print("check1")
            print("user.id: " + str(user.name) + " userId: " + str(username))
            if user.name != username:
                print("check2")
                print(user.get_pokemons_as_json())
                return jsonify(user.get_pokemons_as_json())
                
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return []

    
#-----------------------Battle Handling-----------------------#

# caculate_damage function will return an integer
def calculate_damage(attack_type, attacker, defender):
    total_damage = 0
    if attack_type == 'normal':
        total_damage = int(attacker.pokemon_list[0].attack) - int(defender.pokemon_list[0].defense)
    elif attack_type == 'special':
        sp_atk = int(attacker.pokemon_list[0].sp_atk)
        sp_def = int(defender.pokemon_list[0].sp_def)
        sp_type = attacker.pokemon_list[0].types
        sp_when_attacked = defender.pokemon_list[0].when_attacked
        total_damage = 0
        # Iterate through each type in sp_type list
        for element in sp_type:
            # If the element does not appear in sp_when_attacked list,
            # the multiplier of it is 1
            multiplier = 1  
            for entry in sp_when_attacked:
                if entry['type'] == element:
                    multiplier_str = entry['multiplier']
                    if multiplier_str.endswith('x'):
                        multiplier = int(multiplier_str[:-1])
                    break
            
            damage = sp_atk * multiplier - sp_def
            total_damage += damage
    
    # if total_damage < 0:
    #     total_damage = 0
    return total_damage
    
        
def hp_remained(damage, defender_order):
    # Get the pokemon 
    original_hp = int(users[defender_order].pokemon_list[0].hp)
    original_hp -= damage
    return original_hp


@socketio.on('attack')
def handle_attack(data):
    global current_turn
    attacker_username = data.get('username')
    if not attacker_username:
        emit('error', {'message': 'Invalid attacker username'})
        return

    attacker_order = 0
    defender_order = 1
    if users[0].name == attacker_username:
        attacker = users[0]
        attacker_order = 0
        defender = users[1]
        defender_order = 1
    else:
        attacker = users[1]
        attacker_order = 1
        defender = users[0]
        defender_order = 0

    attack_type = random.choice(['normal', 'special'])
    damage = calculate_damage(attack_type, attacker, defender)
    hp_left = hp_remained(damage, defender_order)
    
    if hp_left < 0:
        hp_left = 0
        
    users[defender_order].pokemon_list[0].hp = str(hp_left)
    defender_pokemons = users[defender_order].pokemon_list
    print(attacker_username + ' used ' + attack_type + ' attack on ' + defender.name + ', dealing ' + str(damage) + ' damage. ' + defender.name + ' Pokémon has ' + defender_pokemons[0].hp + ' HP left.')
    emit('attack_result', {'attacker': attacker_username, 'defender': defender.name, 'attack_type': attack_type, 'damage': str(damage), 'defender_hp': defender_pokemons[0].hp}, broadcast=True)

    # Pokemon of defender die after the attack, 
    # the next pokemon it defender's pokemon_list will be the default
    # If all of the pokemon of defender is dead, game over
    if hp_left == 0 or defender_pokemons[0].hp == '0':
        emit('pokemon_fainted', {'username': defender.name, 'pokemon': users[defender_order].pokemon_list[0].name}, broadcast=True)
        if all(int(p.hp) <= 0 for p in defender.pokemon_list):
            print('game_over')
            emit('game_over', {'winner': attacker_username, 'loser': defender.name}, broadcast=True)
            # Give the pokemons of winner exps
        else:
            for i, poke in enumerate(defender.pokemon_list):
                # If there is an alive pokemon,
                # swap it to position 0 to make it the default
                if int(poke.hp) > 0:
                    temp = users[defender_order].pokemon_list[0]
                    users[defender_order].pokemon_list[0] = users[defender_order].pokemon_list[i]
                    users[defender_order].pokemon_list[i] = temp
                    break
            emit('pokemon_switched', {'username': defender.name, 'pokemon':  users[defender_order].pokemon_list[0].name}, broadcast=True)
            print('switched')
            #Get exp from loser
            accumulated_exp = 0
            for poke in users[defender_order].pokemon_list:
                accumulated_exp += int(poke.exp)
            #
            for i, poke in enumerate(users[attacker_order].pokemon_list):
                new_exp = int(users[attacker_order].pokemon_list[i].exp) + int(accumulated_exp/3)
                users[attacker_order].pokemon_list[i].exp = str(new_exp)

    # Switch turns
    current_turn = defender.name
    emit('turn_change', {'current_turn': current_turn}, broadcast=True)



@socketio.on('switch_pokemon')
def handle_switch_pokemon(data):
    global current_turn
    username = data.get('username')
    pokemonName = data.get('pokemonName')

    if not username or pokemonName is None:
        emit('error', {'message': 'Invalid data for switching Pokemon'})
        return

    player = None
    player_order = 0
    for i, p in enumerate(users):
        if p.name == username:
            player_order = i
            player = p
        else: current_turn = p.name

    for i, poke in enumerate(player.pokemon_list):
        if poke.name == pokemonName:
            temp = users[player_order].pokemon_list[0]
            users[player_order].pokemon_list[0] = users[player_order].pokemon_list[i]
            users[player_order].pokemon_list[i] = temp
            break
        
    emit('pokemon_switched', {'username': username, 'pokemon': users[player_order].pokemon_list[0].name}, broadcast=True)
    emit('turn_change', {'current_turn': current_turn}, broadcast=True)

# -----------------------------------------------------------------------

# Clear session data on the first request after the server starts
@app.before_request
def check_clear_session():
    if app.config['CLEAR_SESSION']:
        session.clear()
        app.config['CLEAR_SESSION'] = False
        
# ----------------------------------------------------------------------

if __name__ == '__main__':
    # Clear the JSON file when the server starts
    clear_json_file()
    # Start the update timer when the server starts
    Timer(1, update_json_file).start()
    # app.run(port=8080)
    socketio.run(app,port=8080,debug=True)
