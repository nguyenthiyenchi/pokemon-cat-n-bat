import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, ElementNotInteractableException

from bs4 import BeautifulSoup
import time
import random

all_types = {
    'normal': 0,
    'fighting': 0,
    'flying': 0,
    'poison': 0,
    'ground': 0,
    'rock': 0,
    'bug': 0,
    'ghost': 0,
    'steel': 0,
    'fire': 0,
    'water': 0,
    'grass': 0,
    'electric': 0,
    'psychic': 0,
    'ice': 0,
    'dragon': 0,
    'dark': 0,
    'fairy': 0,
    'stellar': 0,
    'shadow': 0
}

def fetch_page_with_selenium():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') 
    options.add_argument('--disable-cache')  # Disable caching
    options.add_argument('--disk-cache-size=0')  # Set disk cache size to 0
    options.add_argument('--disable-application-cache')  # Disable application cache
    options.add_argument('--disable-gpu')  # Disable GPU usage
    options.add_argument('--disable-dev-shm-usage')  # Disable /dev/shm usage
    options.add_argument('--no-sandbox')  # Disable sandbox
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    # Now navigate to the main page
    driver.get('https://pokedex.org/#/')


    try:
        # Wait for the Pokémon buttons to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.monster-sprite'))
        )

        # # Find all child elements of id "monsters-list" with type "button" and class "monster-sprite" 
        pokemon_buttons = driver.find_elements(By.CSS_SELECTOR, '#monsters-list button.monster-sprite')

        # Another way to get the buttons
        # pokemon_buttons = driver.find_elements(By.XPATH, '//button[contains(@class, "monster-sprite")]')

        print(len(pokemon_buttons))
        random.shuffle(pokemon_buttons)

        pokedata = []
        for i in range (len(pokemon_buttons)):
            button = pokemon_buttons[i]
            try:
                WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(button)
                )
                button.click()
                time.sleep(1)  # Allow some time for the page to load
            
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '.detail-panel:not(.hidden)'))
                    )
                except TimeoutException:
                    print("Element not found, refreshing page...")
                    driver.refresh()
                    continue

                # Get the page source after clicking the button
                page_source = driver.page_source

                # Parse the page source with BeautifulSoup
                soup = BeautifulSoup(page_source, 'html.parser')

                # Extract Pokémon data
                pokemon = extract_pokemon_data(soup)
                if (len(pokemon)) > 0:
                    pokedata.append(pokemon)
                driver.get('https://pokedex.org/#/')
            except (ElementClickInterceptedException, ElementNotInteractableException, TimeoutException) as e:
                print(f"Error occurred while interacting with element: {e}")

    finally:
        driver.quit()

    return pokedata

def extract_pokemon_data(soup):
    pokemon = soup.select_one('.detail-panel:not(.hidden)')

    if not pokemon:
        return {}

    name = pokemon.select_one('.detail-panel-header').text.strip()
    stats = {stat.select_one('span').text.strip(): stat.select_one('.stat-bar-fg').text.strip() for stat in pokemon.select('.detail-stats-row')}
    species = pokemon.select_one('.monster-species').text.strip()
    description = pokemon.select_one('.monster-description').text.strip()
    profile_data = pokemon.select('.monster-minutia span')
    height = profile_data[0].text.strip()
    weight = profile_data[1].text.strip()
    catch_rate = profile_data[2].text.strip()
    gender_ratios = profile_data[3].text.strip()
    egg_groups = profile_data[4].text.strip().split(',')
    hatch_steps = profile_data[5].text.strip()
    abilities = profile_data[6].text.strip().split(',')
    evs = profile_data[7].text.strip()
    types = [type_tag.text.strip() for type_tag in pokemon.select('.detail-types .monster-type')]
    
    for type in types:
        if (all_types[type] >= 5):
            empty_dict = {}
            return empty_dict
    
    # Add pokemon to its type's categories
    for type in types:
        all_types[type] += 1
    
    when_attacked = []
    for attack_row in pokemon.select('.when-attacked-row'):
        row = {
            'type': attack_row.select_one('.monster-type').text.strip(),
            'multiplier': attack_row.select_one('.monster-multiplier').text.strip()
        }
        when_attacked.append(row)
    
    evolutions = pokemon.select_one('.evolution-label').text.strip() if pokemon.select_one('.evolution-label') else ""
    
    pokemon_dict = {
        'name': name,
        'hp': stats.get('HP', ''),
        'attack': stats.get('Attack', ''),
        'defense': stats.get('Defense', ''),
        'speed': stats.get('Speed', ''),
        'sp_atk': stats.get('Sp Atk', ''),
        'sp_def': stats.get('Sp Def', ''),
        'species': species,
        'description': description,
        'height': height,
        'weight': weight,
        'catch_rate': catch_rate,
        'gender_ratios': gender_ratios,
        'egg_groups': egg_groups,
        'hatch_steps': hatch_steps,
        'abilities': abilities,
        'evs': evs,
        'types': types,
        'when_attacked': when_attacked,
        'evolutions': evolutions,
        'image': None,
        'exp': None
    }

    return pokemon_dict

def main():
    pokedata = fetch_page_with_selenium()

    with open('pokemon_data.json', 'w') as f:
        json.dump(pokedata, f, indent=4)
    print("Pokemon data added to pokemon_data.json\n")

if __name__ == "__main__":
    main()
    print(all_types)
