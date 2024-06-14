import json
from pokebat.pokemon import Pokemon

class Player:
    def __init__(self, name):
        global pokemon_list
        self.name = name
        self.pokemon_list = []
        self.ready = False
        self.active_pokemon = None
        self.id = None

    def load_pokemons_from_json(self, file_path, pokemon_names):
        for name in pokemon_names:
            pokemon = Pokemon()
            pokemon.load_from_json(file_path, name)
            self.pokemon_list.append(pokemon)
        self.active_pokemon = self.pokemon_list[0]

    def set_id(self, player_id):
        self.id = player_id
    

    def choose_pokemon(self, pokemon_indices):
        self.active_pokemon = [self.pokemons[i] for i in pokemon_indices]
        self.ready = True

    def switch_pokemon(self, index):
        self.active_pokemon = self.pokemons[index]
        
    def get_pokemons_as_json(self):
        pokemons_json = [json.loads(pokemon.to_json()) for pokemon in self.pokemon_list]
        return json.dumps(pokemons_json, indent=4)
