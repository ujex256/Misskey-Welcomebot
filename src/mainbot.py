import json
import logging
import pickle
from collections import deque
from threading import Thread

import coloredlogs
import websocket

from logging_styles import set_default

set_default()
import misskey_api as misskey  # NOQA
from ngwords import NGWords  # NOQA
from emojis import EmojiSet  # NOQA


emojis = EmojiSet("response.json")
ngw = NGWords("./ng_words/ngWords.txt")

try:
    with open('./data/users.pickle', "rb") as f:
        have_note_user_ids = pickle.load(f)
except FileNotFoundError:
    have_note_user_ids = deque()

logger = logging.getLogger(__name__)
coloredlogs.install(logger=logger)


# TODO: なんか良い名前に変えたい
def send_welcome(note_id, note_text):
    reaction = emojis.get_response_emoji(note_text)
    Thread(target=misskey.add_reaction, args=(note_id, reaction)).start()
    Thread(target=misskey.renote, args=(note_id,)).start()


def on_message(ws, message):
    global have_note_user_ids
    note_body = json.loads(message)["body"]["body"]
    note_id = note_body["id"]
    note_text = note_body["text"]
    if note_text is None:
        note_text = ""

    # Renote不可ならreturn
    return_flg = False
    if ngw.match(note_text):
        return_flg = True
        logger.info(f"Detected NG word. noteId: {note_id}, word: {ngw.why(note_text)}")
    if misskey.can_reply(note_body):
        return_flg = True
        Thread(target=misskey.reply, args=(note_id, "Pong!")).start()
    if not misskey.can_renote(note_body):
        return_flg = True
    if note_body["userId"] in set(have_note_user_ids):
        return_flg = True
        logger.debug("Skiped api request because it was registered in database.")

    if return_flg:
        return None

    logger.debug(
        f"Notes not registered in database. | body: {note_text} , id: {note_id}"
    )
    user_info = misskey.get_user_info(user_id=note_body["userId"])

    if (notes_count := user_info["notesCount"]) == 1:
        send_welcome(note_id, note_text)
    elif notes_count <= 10:  # ノート数が10以下ならRenote出来る可能性
        notes = misskey.get_user_notes(note_body["userId"], note_id, 10)
        if all([not misskey.can_renote(note) for note in notes]):
            send_welcome(note_id, note_text)
            return

    if notes_count > 5:
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
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"  # NOQA
    SEND_MESSAGE = {"type": "connect", "body": {"channel": "hybridTimeline", "id": "1"}}
    # WebSocketの接続
    ws = websocket.WebSocketApp(
        streaming_api,
        on_message=on_message, on_error=on_error, on_close=on_close,
        header={"User-Agent": USER_AGENT}
    )
    ws.on_open = lambda ws: ws.send(json.dumps(SEND_MESSAGE))
    ws.run_forever()
