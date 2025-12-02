from flask import Flask
from threading import Thread
import time

app = Flask('')


@app.route('/')
def home():
    return "🤖 البوت يعمل على Repl.it!"


def run():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()


if __name__ == '__main__':
    keep_alive()
