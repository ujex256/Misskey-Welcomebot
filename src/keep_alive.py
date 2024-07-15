import asyncio
from multiprocessing import Process

import aiohttp
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
        Process(
            target=run_server,
            args=(str(config.server_host), config.server_port),
        ).start()
        logger.info("Web server started!")

    async def main():
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            await mainbot.Bot(config, session).start_bot()

    asyncio.run(main())
