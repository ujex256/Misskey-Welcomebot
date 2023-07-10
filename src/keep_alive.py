import logging
from multiprocessing import Process
from os import getenv

import coloredlogs
from dotenv import load_dotenv
from flask import Flask, jsonify

import logging_styles
import mainbot


app = Flask("app")

logger = logging.getLogger(__name__)
logging_styles.set_default()
coloredlogs.install(logger=logger)


@app.get("/")
def pong():
    return jsonify({"message": "Pong!"})


def run_server():
    app.run(host="0.0.0.0", port=8080)


if __name__ == "__main__":
    load_dotenv()
    if getenv("RUN_SERVER", False):
        Process(target=run_server).start()
        logger.info("Web server started!")
    mainbot.Bot().start_bot()
