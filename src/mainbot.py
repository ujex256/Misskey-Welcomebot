import threading
import json
import random
import logging
import logging.config
from collections import deque

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
    response_emojis = json.loads(f.read())

have_note_user_ids = deque(db["have_note_user_ids"])
count = 0

logger = logging.getLogger(__name__)
coloredlogs.install(logger=logger)

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
    if note_body["userId"] in set(have_note_user_ids):
        logger.debug("Skiped api request because it was registered in database.")
        return "skipped"

    if not (note_text == ""):
        logger.debug(f"Notes not registered in database. | body: {note_text} , id: {note_id}")
        user_info = misskey.get_user_info(user_id=note_body["userId"])

        if (notes_count := user_info["notesCount"]) == 1:
            for i in response_emojis:
                if any(j in note_text for j in i["keywords"]):
                    if isinstance(i["emoji"], list):
                        reaction = random.choice(i["emoji"])
                        break
                    else:
                        reaction = i["emoji"]
                        break
            else:
                reaction = random.choice(WELCOME_REACTIONS)

            threading.Thread(target=misskey.add_reaction, args=(note_id, reaction,)).start()
            threading.Thread(target=misskey.renote, args=(note_id,)).start()
        elif notes_count > 5:
            global count
            have_note_user_ids.append(user_info["id"])
            count += 1
            if count % 100 == 0 and len(db["have_note_user_ids"]) < 100000:
                misskey.update_db("have_note_user_ids", list(have_note_user_ids), False)
                logger.info(f"DataBase Updated count:{len(db['have_note_user_ids'])}")

def on_error(ws, error):
    logger.warning(str(error))

def on_close(ws, status_code, msg):
    logger.error(f"WebSocket closed. code:{status_code} msg:{msg}")
    bot()


def bot():
    streaming_api = f"wss://{misskey.HOST}/streaming?i={misskey.TOKEN}"
    # WebSocketの接続
    ws = websocket.WebSocketApp(streaming_api, on_message=on_message,
                                on_error=on_error, on_close=on_close,
                                header={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"}
                                )
    ws.on_open = lambda ws: ws.send(
        json.dumps({"type": "connect", "body": {"channel": "hybridTimeline", "id": "1"}})
    )
    ws.run_forever()
