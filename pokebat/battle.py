import random
from pokebat.player import Player
from pokebat.pokemon import Pokemon

class Battle:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.current_turn = None
        self.battle_log = []

    def start_battle(self):
        self.turn = self.determine_turn()
        self.battle_log.append(f"Battle started between {self.player1.name} and {self.player2.name}")

    def determine_turn(self):
        if self.player1.active_pokemon.speed > self.player2.active_pokemon.speed:
            return self.player1
        else:
            return self.player2

    def attack(self, attacker, defender):
        attack_type = "normal" if random.choice([True, False]) else "special"
        if attack_type == "normal":
            dmg = int(attacker.active_pokemon["attack"]) - int(defender.active_pokemon["defense"])
        else:
            dmg = int(attacker.active_pokemon["sp_atk"]) - int(defender.active_pokemon["sp_def"])
        
        defender.active_pokemon["hp"] = str(max(0, int(defender.active_pokemon["hp"]) - dmg))
        
        if int(defender.active_pokemon["hp"]) <= 0:
            self.battle_log.append(f"{defender.active_pokemon['name']} fainted!")
            self.auto_switch(defender)
        
        self.battle_log.append(f"{attacker.active_pokemon['name']} used {attack_type} attack on {defender.active_pokemon['name']}, dealing {dmg} damage.")
        self.turn = self.player2 if self.turn == self.player1 else self.player1

    def auto_switch(self, player):
        remaining_pokemons = [p for p in player.pokemons if int(p["hp"]) > 0]
        if remaining_pokemons:
            player.active_pokemon = remaining_pokemons[0]
            self.battle_log.append(f"{player.name} switched to {player.active_pokemon['name']}.")
        else:
            self.battle_log.append(f"{player.name} has no remaining Pokémon. {self.player1.name if player == self.player2 else self.player2.name} wins the battle!")
            return "end"
