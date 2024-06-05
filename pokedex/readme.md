# Set Up
## Packages to Install
1. selenium: This is required for automating web browser interaction.
2. webdriver-manager: This helps in automatically managing the WebDriver binaries for you.
3. beautifulsoup4: This is for parsing HTML content.
4. lxml: This is often used as a parser for BeautifulSoup for better performance.

## Installation Commands
The implementation use Python so you can install all of these packages using pip. Run the following commands in your terminal or command prompt:
```
pip install selenium
pip install webdriver-manager
pip install beautifulsoup4
pip install lxml
```

## Additional Setup
1. Google Chrome: Ensure that Google Chrome is installed on your machine, as webdriver-manager will download the appropriate ChromeDriver for it.
2. ChromeDriver: The webdriver-manager package will automatically handle the installation of ChromeDriver, but you need to ensure you have internet access for the download.

# Process
## Crawling Pokemons' Details
- **data_scrapper.py** is the implementation of Pokemon data crawler.
- **image_exp_crawl.py** is for crawling Pokemons' image URL, and default EXP. 
 
Please run *data_scrapper.py* first to initialize the JSON database - *pokemon_data.json*, and then *image_exp_crawl.py*, to update the missing values of Pokemons in the JSON file, and finally save it to the complete file called *pokemon_data_full.json*. These files can be run using the following commands:
```
python3 data_scrapper.py
python3 image_exp_crawl.py
```
