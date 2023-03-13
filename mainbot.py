import json
import os
import random
import threading
import logging
import logging.config
from collections import deque

import websocket
from replit import db

from ngwords import NGWords
from note_action import renote, add_reaction, update_db, get_user_info


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
_ng = NGWords("ng_words/ngWords.txt")
with open("response.json", "r", encoding="utf8") as f:
    response_emojis = json.loads(f.read())

have_note_user_ids = deque(db["have_note_user_ids"])
count = 0

logging.config.fileConfig("logging.ini")
logger = logging.getLogger(__name__)

def bot():
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
            logger.debug("Skiped api request because it was registered in \"DB\"")
            return "skipped"

        if not (note_text == ""):
            print(note_text)
            user_info = get_user_info(user_id=note_body["userId"])

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

                threading.Thread(target=add_reaction, args=(note_id, reaction,)).start()
                threading.Thread(target=renote, args=(note_id,)).start()
            elif notes_count > 5:
                global count
                have_note_user_ids.append(user_info["id"])
                count += 1
                if count % 100 == 0 and len(db["have_note_user_ids"]) < 100000:
                    update_db("have_note_user_ids", list(set(have_note_user_ids)), False)
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
