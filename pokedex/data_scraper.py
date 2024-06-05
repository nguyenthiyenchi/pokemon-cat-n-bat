import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, ElementNotInteractableException, StaleElementReferenceException

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
    # Turn off (comment) this line to see the interactions:
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
        # Wait for the Pokémon <button> with class name 'monster-sprite' to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.monster-sprite'))
        )
        # If it out of 10 seconds, but the HTML Inspect of page hasn't loaded, move to finally part of this function
        
        pokedata = []
        all_buttons = [] # all <button> attributes have class 'monster-sprite' that have clicked
        scroll_pause_time = 2 # Time to wait after each scroll
        
        # Get the height of a pokemon button
        button_height = driver.execute_script("return document.querySelector('#monsters-list button.monster-sprite').offsetHeight")
        
        # Initially scroll down a bit
        current_height = button_height*1.5

        batch_count = 0
        # Find all child elements of id "monsters-list" with type "button" and class "monster-sprite" 
        driver.execute_script("window.scrollBy(0, arguments[0]);", current_height)

        while True:
            # Find the pokemon button's element in the html source
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.monster-sprite'))
            )
            pokemon_buttons = driver.find_elements(By.CSS_SELECTOR, '#monsters-list button.monster-sprite')
            batch_count +=1
            
            # Get the number of buttons and looping through them
            print("Batch " + str(batch_count) + ": " + str(len(pokemon_buttons)))
            
            for i in range (30): # The number of button to click
                # Take the actual button
                button = pokemon_buttons[i]
                
                # Check if the button was clicked or not
                if button not in all_buttons:
                    # If not, add it to the list of clicked buttons
                    all_buttons.append(button)
                    
                    try: 
                        # Wait at most 5s to make sure that button is clickable
                        WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable(button)
                        )

                        # Click the button
                        button.click()
                        print("Pokemon " + str(i+1) + " is clicked")
                        time.sleep(1)  # Allow some time for the page to load
                        
                        try:
                            #Wait at most 10s for the detail panel to load and show up
                            WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, '.detail-panel:not(.hidden)'))
                            )
                        except TimeoutException:
                            print("Element not found, TimeoutException occurred")
                            # driver.refresh()
                            continue

                        # Get the page source after clicking the button (F12 on keyboard)
                        page_source = driver.page_source
                        
                        # Parse the page source with BeautifulSoup
                        soup = BeautifulSoup(page_source, 'html.parser')
                        
                        # Extract Pokémon data
                        pokemon = extract_pokemon_data(soup)
                        if (len(pokemon)) > 0:
                            pokedata.append(pokemon)

                        # After finished extracting information from pokemon detail panel,
                        # clicking the back button will navigate user to the top of the website
                        # Here we load the page again to make sure everything works fine
                        driver.get('https://pokedex.org/#/')

                        # Scroll the website back to the current height, from the top of the website
                        driver.execute_script("window.scrollBy(0, arguments[0]);", current_height)
                        
                        # Wait for new content to load
                        time.sleep(scroll_pause_time)
                        
                        # Reload the buttons to use inside the for loop
                        pokemon_buttons = driver.find_elements(By.CSS_SELECTOR, '#monsters-list button.monster-sprite')
                        
                    except (ElementClickInterceptedException, ElementNotInteractableException, StaleElementReferenceException, TimeoutException) as e:
                        print(f"Error occurred while interacting with element: {e}")
                        print(button)

            # Scroll down by the height of 18 lines of buttons, from the current height
            # The number 18 is calculate from: 
            # The largest amount of buttons that can be show up at a time / The number of buttons in a line
            current_height += button_height*18
            driver.execute_script("window.scrollBy(0, arguments[0]);",  button_height*18)

            # Wait for new content to load
            time.sleep(scroll_pause_time)

            # Check if new buttons are loaded by comparing the current number of buttons
            new_buttons = driver.find_elements(By.CSS_SELECTOR, '#monsters-list button.monster-sprite')
            if new_buttons == pokemon_buttons:
                print("Done")
                break  # Break the loop if no new buttons are loaded
            
    finally:
        driver.quit()

    # Random to save in json not in order
    random.shuffle(pokedata)

    return pokedata

def extract_pokemon_data(soup):
    # Get the element of class '.detail-panel' and not hidden
    pokemon = soup.select_one('.detail-panel:not(.hidden)')
    if not pokemon: # If there is no such element
        return {}

    # Extracting data:
    # - Name
    name = pokemon.select_one('.detail-panel-header').text.strip()
    
    # - HP, Attack, Defense, Speed, Sp Atk, Sp Def
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
    
    # - Elemental Types
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