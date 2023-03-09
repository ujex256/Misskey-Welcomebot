import json
import os
import random
import threading
import logging
from collections import deque

import requests
import websocket
from requests.exceptions import Timeout

from replit import db

HOST = "misskey.io"
TOKEN = os.environ["MISSKEY-ACCESSTOKEN"]

WELCOME_REACTIONS = [
    ":youkoso:",
    ":youkoso_send_money:",
    ":send_money:",
    ":nyanpuppu:",
    ":supertada:",
    ":yorosiku_onegai:",
]
with open("ngwords.txt", "r", encoding="utf8") as f:
    words = f.read()
    NG_WORDS = [i for i in words.split("\n") if (i[0] != "-") and (i[0] != "#")]
    EXCLUDED_WORDS = [i[1:] for i in words.split("\n") if i[0] == "-"]

have_note_user_ids = deque(db["have_note_user_ids"])
count = 0

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s",
                                       "%Y-%m-%d %H:%M"
                     ))
logger.addHandler(handler)


def renote(note_id: str):
    res = requests.post(
        f"https://{HOST}/api/notes/create",
        json={
            "localOnly": True,
            "renoteId": note_id,
            "i": TOKEN,
        },
    )
    if res.status_code >= 200 and res.status_code < 300:
        logger.info(f"Renoted! noteId: {note_id}")
    else:
        logger.error(f"Renote failed noteId: {note_id}, msg: {res.text}")

def add_reaction(note_id: str, reaction: str):
    res = requests.post(
        f"https://{HOST}/api/notes/reactions/create",
        json={
            "noteId": note_id,
            "reaction": reaction,
            "i": TOKEN,
        },
    )
    if res.status_code >= 200 and res.status_code < 300:
        logger.info(f"Reaction added noteId: {note_id}, reaction: {reaction}")
    else:
        logger.error(f"Failed to add reaction noteId: {note_id}, msg: {res.text}")

def update_replit_db(key: str, value, allow_duplicates: bool=True):
    if isinstance(value, deque):
        value = list(value)
    if not allow_duplicates and isinstance(value, list):
        value = list(set(value))
    db[key] = value

def bot():
    def on_message(ws, message):
        global have_note_user_ids
        note_body = json.loads(message)["body"]["body"]
        note_id = note_body["id"]
        note_text = note_body["text"]
        if note_text is None:
            note_text = ""

        if any(x in note_text for x in NG_WORDS) and (not any(x in note_text for x in EXCLUDED_WORDS)):
            logger.info("Detected NG word")
            return "ng word detected"
        if note_body["userId"] in list(have_note_user_ids):
            logger.debug("Skiped api request because it was registered in \"DB\"")
            return "skipped"

        if not (note_text == ""):
            print(note_text)
            try:
                user_info = requests.post(
                    f"https://{HOST}/api/users/show",
                    json={
                        "username": note_body["user"]["username"],
                        "i": TOKEN,
                    },
                    timeout=5,
                )
            except Timeout:
                logger.warning("api timeout")

            if (notes_count := user_info.json()["notesCount"]) == 1:
                if "レターパック" in note_text or ":5000" in note_text:
                    reaction = ":send_money:"
                elif "yosano" in note_text or "与謝野晶子" in note_text:
                    reaction = ":yosano_akiko_is_always_watching_you:"
                elif ":send_money:" in note_text:
                    reaction = ":is_all_scam:"
                elif "ろぐぼ" in note_text:
                    reaction = ":opera:"
                else:
                    reaction = random.choice(WELCOME_REACTIONS)

                threading.Thread(target=add_reaction, args=(note_id, reaction,)).start()
                threading.Thread(target=renote, args=(note_id,)).start()
            elif notes_count > 5:
                global count
                have_note_user_ids.append(user_info.json()["id"])
                count += 1
                if count % 100 == 0 and len(db["have_note_user_ids"]) < 100000:
                    update_replit_db("have_note_user_ids", list(set(have_note_user_ids)), False)
                    logger.info(f"DataBase Updated count:{len(db['have_note_user_ids'])}")

    def on_error(ws, error):
        logger.warning(str(error))

    def on_close(ws, status_code, msg):
        logger.error(f"WebSocket closed. code:{status_code} msg:{msg}")
        bot()

    streaming_api = f"wss://{HOST}/streaming?i={TOKEN}"
    # WebSocketの接続
    ws = websocket.WebSocketApp(streaming_api, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = lambda ws: ws.send(
        json.dumps({"type": "connect", "body": {"channel": "localTimeline", "id": "1"}})
    )
    ws.run_forever()
