import json
import random
import logging
from collections import deque
from threading import Thread

import websocket
import coloredlogs
from replit import db

from .logging_styles import set_default

set_default()
from .ngwords import NGWords
from . import misskey_api as misskey


WELCOME_REACTIONS = [
    ":youkoso:",
    ":youkoso_send_money:",
    ":send_money:",
    ":nyanpuppu:",
    ":supertada:",
    ":yorosiku_onegai:",
]
_ng = NGWords("./ng_words/ngWords.txt")
with open("./response.json", "r", encoding="utf8") as f:
    response_emojis = json.load(f)

try:
    have_note_user_ids = deque(db["have_note_user_ids"])
except:
    have_note_user_ids = deque()

logger = logging.getLogger(__name__)
coloredlogs.install(logger=logger)

# TODO: なんか良い名前に変えたい
def send_welcome(note_id, note_text):
    for i in response_emojis:
        if any(j in note_text for j in i["keywords"]):
            if isinstance(i["emoji"], list):
                reaction = random.choice(i["emoji"])
            else:
                reaction = i["emoji"]
            break
    else:
        reaction = random.choice(WELCOME_REACTIONS)

    Thread(target=misskey.add_reaction, args=(note_id, reaction)).start()
    Thread(target=misskey.renote, args=(note_id,)).start()


def on_message(ws, message):
    global have_note_user_ids
    note_body = json.loads(message)["body"]["body"]
    note_id = note_body["id"]
    note_text = note_body["text"]
    if note_text is None:
        note_text = ""

    if _ng.match(note_text):
        logger.info(f"Detected NG word. noteId: {note_id}, word: {_ng.why(note_text)}")
        return "ng word detected"
    if ("/ping" in note_text) and (f"@{misskey.USERNAME}" in note_text or note_body["visibility"] == "specified"):
        Thread(target=misskey.reply, args=(note_id, "Pong!")).start()
        return "replied"

    if not misskey.is_valid_note(note_body):
        return "no"
    if note_body["userId"] in set(have_note_user_ids):
        logger.debug("Skiped api request because it was registered in database.")
        return "skipped"

    logger.debug(
        f"Notes not registered in database. | body: {note_text} , id: {note_id}"
    )
    user_info = misskey.get_user_info(user_id=note_body["userId"])

    if (notes_count := user_info["notesCount"]) == 1:
        send_welcome(note_id, note_text)
    elif notes_count > 5:
        if notes_count <= 10:
            notes = misskey.get_user_notes(note_body["userId"], note_id, 10)
            if all([not misskey.is_valid_note(note) for note in notes]):
                send_welcome(note_id, note_text)
                return
        have_note_user_ids.append(note_body["userId"])
        if (count := len(have_note_user_ids)) % 100 == 0 and count < 100000:
            misskey.update_db("have_note_user_ids", have_note_user_ids, False)
            logger.info(f"DataBase Updated. count: {count}")

def on_error(ws, error):
    logger.warning(str(error))

def on_close(ws, status_code, msg):
    logger.error(f"WebSocket closed. code:{status_code} msg:{msg}")
    bot()


def bot():
    streaming_api = f"wss://{misskey.HOST}/streaming?i={misskey.TOKEN}"
    # WebSocketの接続
    ws = websocket.WebSocketApp(
        streaming_api,
        on_message=on_message, on_error=on_error, on_close=on_close,
        header={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
        },
    )
    ws.on_open = lambda ws: ws.send(
        json.dumps(
            {"type": "connect", "body": {"channel": "hybridTimeline", "id": "1"}}
        )
    )
    ws.run_forever()
