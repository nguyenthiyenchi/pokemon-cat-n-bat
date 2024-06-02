import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup


def fetch_page_with_selenium(url):
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless') 
    options.add_argument('--disable-cache')  # Disable caching
    options.add_argument('--disk-cache-size=0')  # Set disk cache size to 0
    options.add_argument('--disable-application-cache')  # Disable application cache
    options.add_argument('--disable-gpu')  # Disable GPU usage
    options.add_argument('--disable-dev-shm-usage')  # Disable /dev/shm usage
    options.add_argument('--no-sandbox')  # Disable sandbox
    # options.add_experimental_option('prefs', {'cache.disable': True, 'disk_cache_size': 0})  # Disable browser cache
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    # Now navigate to the target URL
    driver.get(url)
    driver.refresh()
    
    # Refresh the page to trigger dynamic loading
    driver.get(url)
    driver.refresh()

    try:
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.detail-panel:not(.hidden)'))
        )
    except TimeoutException:
        print("Element not found, refreshing page...")
        driver.refresh()

    page_source = driver.page_source
    driver.quit()

    return page_source

def extract_pokemon_data(soup):
    # pokemon_data = []
    pokemon = soup.select_one('.detail-panel:not(.hidden)')

    print(pokemon)
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
    types = [type_tag.text.strip() for type_tag in pokemon.select('.monster-type')]
    
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
    
    # pokemon_data.append(pokemon_dict)
    
    return pokemon_dict

def main():


    types = {
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
    pokedata = []


    for order in range (1, 3):
        url = "https://pokedex.org/#/pokemon/" + str(order) 
        print(url)
        page_source = fetch_page_with_selenium(url)
        soup = BeautifulSoup(page_source, 'html.parser')
        # print(soup)

        pokemon = extract_pokemon_data(soup)
        pokedata.append(pokemon)
        # with open('./{}.txt'.format("pokemon_data" + str(order)), mode='wt', encoding='utf-8') as file:
        #     file.write(str(soup))
    
    with open('pokemon_data.json', 'w') as f:
        json.dump(pokedata, f, indent=4)
    print("Pokemon data added to pokemon_data.json\n")

if __name__ == "__main__":
    main()
