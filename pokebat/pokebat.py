from pokebat.battle import Battle

class PokeBat:
    def __init__(self, player1, player2):
        self.battle = Battle(player1, player2)

    def execute_turn(self):
        if not self.battle.turn:
            self.battle.start_battle()

        attacker = self.battle.turn
        defender = self.battle.player2 if self.battle.turn == self.battle.player1 else self.battle.player1

        self.battle.attack(attacker, defender)
        return self.battle.battle_log

