import multiprocessing
from flask import Flask
from replit import web

from src.mainbot import bot

if __name__ == "__main__":
    app = Flask(__name__)

    @app.route('/')
    def index():
        return 'Pong'

    p = multiprocessing.Process(target=bot)
    p.start()
    web.run(app)
