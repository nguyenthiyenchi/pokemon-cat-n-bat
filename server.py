from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/hello', methods=['POST'])
def hello_handler():
    if request.method != 'POST':
        return jsonify({'error': 'Invalid request method'}), 405

    name = request.form.get('name')
    if not name:
        return jsonify({'error': 'Error parsing form data'}), 400

    print("Received data:", name)
    return f"Hello, {name}!", 200

if __name__ == '__main__':
    app.run(port=8080)
