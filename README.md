# Pokemon: Catching and Battling

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