from multiprocessing import Process
from os import getenv

from dotenv import load_dotenv
from flask import Flask, jsonify

from mainbot import start_bot

app = Flask(__name__)


@app.get("/")
def pong():
    return jsonify({"message": "Pong!"})


if __name__ == "__main__":
    load_dotenv()
    if getenv("RUN_SERVER", False):
        Process(lambda x: app.run()).start()
    start_bot()
