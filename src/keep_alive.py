import asyncio
from multiprocessing import Process

from flask import Flask, jsonify

import logging_styles
import mainbot
import environs


app = Flask("app")

logger = logging_styles.getLogger(__name__)


@app.get("/")
def pong():
    return jsonify({"message": "Pong!"})


def run_server():
    app.run(host="0.0.0.0", port=8080)


if __name__ == "__main__":
    config = environs.Settings()
    if config.run_server:
        Process(target=run_server).start()
        logger.info("Web server started!")
    asyncio.run(mainbot.Bot(config).start_bot())
