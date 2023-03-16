import multiprocessing
from flask import Flask

from src.mainbot import bot

app = Flask(__name__)

p = multiprocessing.Process(target=bot)
p.start()


@app.route('/')
def index():
    return 'Pong'


app.run(host='0.0.0.0', port=81)
