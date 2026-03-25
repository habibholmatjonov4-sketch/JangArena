from flask import Flask
from threading import Thread
import logging

app = Flask(__name__)
logging.getLogger('werkzeug').setLevel(logging.ERROR)

@app.route('/')
def home():
    return "🤖 Bot ishlamoqda!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    """Keep the bot alive"""
    t = Thread(target=run)
    t.daemon = True
    t.start()
    print("🌐 Web server ishladi! Bot doimiy ishlaydi.")