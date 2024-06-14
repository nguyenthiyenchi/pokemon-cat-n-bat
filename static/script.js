document.addEventListener("DOMContentLoaded", function() {
    // ----------------------------------- Ready Interface
    var username = 'u1'; // Adjust this dynamically for each player
    // const readyButton = document.querySelector('.ready-button');
    const selectElements = document.querySelectorAll('select');

    const socket = io();
    var player_id;

    socket.on('connect', function() {
        console.log('Connected to server');
        player_id = socket.id
    });

    fetch(`/get_pokemon_list/${username}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error(data.error);
            } else {
                populateSelectElements(data);
            }
        });

    function populateSelectElements(pokemons) {
        selectElements.forEach(select => {
            pokemons.forEach(pokemon => {
                const option = document.createElement('option');
                option.value = pokemon.name;
                option.text = pokemon.name;
                select.appendChild(option);
            });
        });
    }
    
    function confirmReady() {
        const usernameInput = document.getElementById('name-input');
        username = usernameInput.value;
        const readyButton = document.getElementById('readyButton');
        const selectedPokemons = Array.from(selectElements).map(select => select.value);
        console.log(selectedPokemons.length);
        // Check for duplicates
        if (new Set(selectedPokemons).size !== selectedPokemons.length ) {
            alert("Please select 3 different Pokémon.");
            return;
        }
        readyButton.disabled = true;

        fetch('/ready', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, player_id, selectedPokemons })
        }).then(response => response.json())
        .then(data => {
            console.log(data.status);
        });
    }

    document.getElementById('readyButton').addEventListener('click', () => {
        confirmReady();
    });

    socket.on('connect', function() {
        console.log('Connected to server');
    });

    socket.on('battle_ready', function(data) {
        console.log(data.message);
        window.location.href = '/battle';
      
    });

    // ----------------------------------- Battle Interface
    // const socket = io();
    // const userId = socket.id;
    // var currentUsername;
    const pokemonElements = document.getElementsByClassName('pokemon')
    const opponent_pokemonElements = document.getElementsByClassName('opponent-pokemon')

    fetch(`/get_battle_pokemon_list/${username}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error(data.error);
            } else {
                console.log(data)
                populatePokemonElements(data, 0);
            }
        });

    fetch(`/get_battle_opponent_pokemon_list/${username}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error(data.error);
            } else {
                populatePokemonElements(data, 1);
            }
        });

    socket.on('take_turn', (data) => {
        currentUsername = data.username;
        document.getElementById('attack-btn').disabled = false;
    });

    function populatePokemonElements(pokemons, isOpponent) {
        var pokemonElementsList;
        if (isOpponent == 0) {
            pokemonElementsList = pokemonElements;
        } else {
            pokemonElementsList = opponent_pokemonElements;
        }
        for (let i = 0; i < pokemonElementsList.length; i++) {
            if (i < pokemons.length) {
                const pokemonElement = pokemonElementsList[i];
                pokemonElement.querySelector('.pokemon-name').textContent = `Name: ${pokemons[i].name}`;
                pokemonElement.querySelector('.pokemon-hp').textContent = `HP: ${pokemons[i].hp}`;
                const pokemonImageElement = pokemonElement.querySelector('.pokemon-image');
                pokemonImageElement.style.backgroundImage = `url(${pokemons[i].image})`;
                pokemonImageElement.style.backgroundSize = 'cover';
                pokemonImageElement.style.backgroundPosition = 'center';
                
            }
        }

        console.log("checkpoint")
    }


    document.getElementById('attack-btn').addEventListener('click', () => {
        socket.emit('attack', { username: currentUsername });
    });

    // Adding event listener to each element with class 'pokemon-switch'
    const switchElements = document.querySelectorAll('.pokemon-switch');
    switchElements.forEach(element => {
        element.addEventListener('click', (event) => {
            const clickedElement = event.currentTarget;
            const pokemonName = clickedElement.querySelector('.pokemon-name').textContent;
            const pokemonHp = clickedElement.querySelector('.pokemon-hp').textContent;

            console.log(`Pokemon Name: ${pokemonName}`);
            console.log(`Pokemon HP: ${pokemonHp}`);

            // Sending message to server to update user's pokemon list in server
            socket.emit('switch', { username: currentUsername, pokemonName: pokemonName, pokemonHP: pokemonHp});
        });
    });
});
