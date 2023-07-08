import logging
from multiprocessing import Process
from os import getenv

import coloredlogs
from dotenv import load_dotenv
from flask import Flask, jsonify

import logging_styles
from mainbot import start_bot


app = Flask(__name__)

logger = logging.getLogger(__name__)
logging_styles.set_default()
coloredlogs.install(logger=logger)


@app.get("/")
def pong():
    return jsonify({"message": "Pong!"})


if __name__ == "__main__":
    load_dotenv()
    if getenv("RUN_SERVER", False):
        Process(lambda x: app.run()).start()
        logging.info("Web server started!")
    start_bot()
