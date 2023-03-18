import multiprocessing
from flask import Flask
from replit import web

from src.mainbot import bot

app = Flask(__name__)

p = multiprocessing.Process(target=bot)
p.start()


@app.route('/')
def index():
    return 'Pong'

web.run(app)
