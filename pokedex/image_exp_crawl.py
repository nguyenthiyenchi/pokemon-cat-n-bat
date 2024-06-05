import json
import requests
from bs4 import BeautifulSoup

# Load the JSON file
with open('pokemon_data.json', 'r') as file:
    pokemon_data = json.load(file)

# URL of the Bulbapedia page
url = "https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_effort_value_yield_(Generation_IX)"

# Fetch the HTML content from the Bulbapedia page
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Extract the rows containing Pokémon data
rows = soup.find_all('tr', {'style': 'text-align: center; background:#FFF'})

cnt = 0

# Function to get image URL and exp for a Pokémon name
def get_pokemon_data(pokemon_name):
    for row in rows:
        name_cell = row.find('td', {'class': 'l'})
        if name_cell and pokemon_name.lower() in name_cell.text.lower():
            image_cell = row.find('img')
            exp_cell = row.find_all('td')[3]
            image_url = image_cell['src'] if image_cell else None
            exp = exp_cell.text.strip() if exp_cell else None
            return image_url, exp
    return None, None

# Loop through the Pokémon data and update with image URL and exp
for pokemon in pokemon_data:
    name = pokemon['name']
    image_url, exp = get_pokemon_data(name)
    if image_url:
        pokemon['image'] = image_url
    if exp:
        pokemon['exp'] = exp

# Save the updated JSON data back to the file
with open('pokemon_data_full.json', 'w') as file:
    json.dump(pokemon_data, file, indent=4)

print("Pokemon data updated successfully.")
