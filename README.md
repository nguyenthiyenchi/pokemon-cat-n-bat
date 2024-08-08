<h5 align="center" style="font-weight: 700;">INTERNATIONAL UNIVERSITY - VNUHCM
<br>
<div style="color: rgb(98, 98, 98);">DATA STRUCTURE & ALGORITHM</div>
</h5>
<div id="top" align ="center">
    <img src="./resources/forReadme/banner.gif" alt="Banner">
</div>

...

<div align="center">    
    <h1>Pokemon: Catching and Battling</h1>    
    <strong>Pokemon: Catching and Battling</strong> is a dynamic multiplayer game that uses technologies like HTML, CSS, JavaScript, Flask, and Python to allow players to work together in a shared world to catch Pokémon. It also has a unique battle mode that lets two players battle Pokémon one-on-one at once.
</div>   
<br>

# Table of Content :clipboard:

1. [Introduction](#introduction)
2. [Team members](#team-members)
3. [System design and Modeling](#system-design-and-modeling)
4. [UI Interface](#ui-interface)
5. [Installation](#installation)
6. [How to play](#how-to-play)
7. [References](#references)

`app.py` is a sample of client, index.html is the interface of client of `app.py`

#### Need to install:
- `pip install flask` (<strong>This is important</strong>)
- `pip install flask-cors` (This is in test)
<br>

#### After install `flask`, you need to the `FLASK_APP` environment variable to point to your `server.py`:
- On Window (Command Prompt):
`$env:FLASK_APP = "server.py"`
- On Windows (PowerShell):
`set FLASK_APP=server.py`
- On macOS/Linux:
`export FLASK_APP=server.py`
<br>
- Then run `flask run --port 8080`