from flask import Flask, render_template
from threading import Thread

app = Flask(__name__, template_folder='web', static_folder='web', static_url_path='')

@app.route('/')
def index():
    return render_template('index.html')

def run():
    app.run(host='0.0.0.0', port=8000)

def keep_alive():
    server = Thread(target=run)
    server.start()