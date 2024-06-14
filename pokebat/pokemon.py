import json

class Pokemon:
    def __init__(self, name=None, hp=None, attack=None, defense=None, speed=None, sp_atk=None, sp_def=None, species=None, description=None, height=None, weight=None, catch_rate=None, gender_ratios=None, egg_groups=None, hatch_steps=None, abilities=None, evs=None, types=None, when_attacked=None, evolutions=None, image=None, exp=None):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.sp_atk = sp_atk
        self.sp_def = sp_def
        self.species = species
        self.description = description
        self.height = height
        self.weight = weight
        self.catch_rate = catch_rate
        self.gender_ratios = gender_ratios
        self.egg_groups = egg_groups
        self.hatch_steps = hatch_steps
        self.abilities = abilities
        self.evs = evs
        self.types = types
        self.when_attacked = when_attacked
        self.evolutions = evolutions
        self.image = image
        self.exp = exp

    def load_from_json(self, file_path, pokemon_name):
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        for pokemon in data:
            if pokemon['name'].lower() == pokemon_name.lower():
                self.name = pokemon['name']
                self.hp = pokemon['hp']
                self.attack = pokemon['attack']
                self.defense = pokemon['defense']
                self.speed = pokemon['speed']
                self.sp_atk = pokemon['sp_atk']
                self.sp_def = pokemon['sp_def']
                self.species = pokemon['species']
                self.description = pokemon['description']
                self.height = pokemon['height']
                self.weight = pokemon['weight']
                self.catch_rate = pokemon['catch_rate']
                self.gender_ratios = pokemon['gender_ratios']
                self.egg_groups = pokemon['egg_groups']
                self.hatch_steps = pokemon['hatch_steps']
                self.abilities = pokemon['abilities']
                self.evs = pokemon['evs']
                self.types = pokemon['types']
                self.when_attacked = pokemon['when_attacked']
                self.evolutions = pokemon['evolutions']
                self.image = pokemon['image']
                self.exp = pokemon['exp']
                return
        
        print(f"Pokémon named '{pokemon_name}' not found in the file.")

    def print_info(self):
        print(f"Name: {self.name}")
        print(f"Species: {self.species}")
        print(f"Description: {self.description}")
        print(f"Height: {self.height}")
        print(f"Weight: {self.weight}")
        print(f"HP: {self.hp}")
        print(f"Attack: {self.attack}")
        print(f"Defense: {self.defense}")
        print(f"Speed: {self.speed}")
        print(f"Special Attack: {self.sp_atk}")
        print(f"Special Defense: {self.sp_def}")
        print(f"Catch Rate: {self.catch_rate}")
        print(f"Gender Ratios: {self.gender_ratios}")
        print(f"Egg Groups: {', '.join(self.egg_groups)}")
        print(f"Hatch Steps: {self.hatch_steps}")
        print(f"Abilities: {', '.join(self.abilities)}")
        print(f"EVs: {self.evs}")
        print(f"Types: {', '.join(self.types)}")
        print("When Attacked: " + ', '.join([f"{wa['type']}: {wa['multiplier']}" for wa in self.when_attacked if wa['type']]))

        print(f"Evolutions: {self.evolutions}")
        print(f"Experience: {self.exp}")
        print(f"Image URL: {self.image}")

    def to_json(self):
        data = {
            "name": self.name,
            "hp": self.hp,
            "attack": self.attack,
            "defense": self.defense,
            "speed": self.speed,
            "sp_atk": self.sp_atk,
            "sp_def": self.sp_def,
            "species": self.species,
            "description": self.description,
            "height": self.height,
            "weight": self.weight,
            "catch_rate": self.catch_rate,
            "gender_ratios": self.gender_ratios,
            "egg_groups": self.egg_groups,
            "hatch_steps": self.hatch_steps,
            "abilities": self.abilities,
            "evs": self.evs,
            "types": self.types,
            "when_attacked": self.when_attacked,
            "evolutions": self.evolutions,
            "image": self.image,
            "exp": self.exp
        }
        return json.dumps(data, indent=4)
    

# pokemon1 = Pokemon()
# pokemon1.load_from_json("../u1.json","Raichu")
# print(pokemon1.types)

# print(pokemon1.when_attacked)


# # Get the elements from the list 'type' 
# # then check for these element's multipliers 
# # from the list 'sp_when_attacked'
# # If not found, the multiplier = 1

# sp_type = ['electric']
# sp_when_attacked = [{'type': 'ground', 'multiplier': '2x'}, {'type': '', 'multiplier': ''}, {'type': '', 'multiplier': ''}]
