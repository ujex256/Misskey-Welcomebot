import asyncio
from multiprocessing import Process

from flask import Flask, jsonify

import environs
import logging_styles
import mainbot

app = Flask("app")

logger = logging_styles.getLogger(__name__)


@app.get("/")
def pong():
    return jsonify({"message": "Pong!"})


def run_server(host: str, port: int):
    app.run(host=host, port=port)


if __name__ == "__main__":
    config = environs.Settings()
    if config.run_server:
        Process(target=run_server, args=(str(config.server_host), config.server_port)).start()
        logger.info("Web server started!")
    asyncio.run(mainbot.Bot(config).start_bot())
