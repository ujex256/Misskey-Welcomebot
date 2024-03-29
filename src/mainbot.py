import json
import logging
import os
from threading import Thread

import coloredlogs
import websocket

import utils
import logging_styles
import misskey_api as misskey
from ngwords import NGWords
from emojis import EmojiSet


class Bot:
    counter = utils.Counter(100, lambda: None)

    def __init__(self, restart: bool = True) -> None:
        logger = logging.getLogger(__name__)
        logging_styles.set_default()
        coloredlogs.install(logger=logger)
        self.logger = logger
        self._restart = restart

        self.config_dir = utils.config_dir()

        logger.info("Loading response.json...")
        self.emojis = EmojiSet(os.path.join(self.config_dir, "response.json"))
        logger.info("Loading ngwords.txt...")
        self.ngw = NGWords(os.path.join(self.config_dir, "ngwords.txt"))

        self.db = utils.get_db()

    # TODO: なんか良い名前に変えたい
    def send_welcome(self, note_id: str, note_text: str) -> None:
        """Send welcome message.

        Args:
            note_id (str): misskey note id
            note_text (str): misskey note text
        """
        reaction = self.emojis.get_response_emoji(note_text)
        Thread(target=misskey.add_reaction, args=(note_id, reaction)).start()
        Thread(target=misskey.renote, args=(note_id,)).start()

    @counter
    def need(self) -> bool:
        if self.counter._now == 0:
            return True
        return False

    def on_message(self, ws, message: str) -> None:
        note_body = json.loads(message)["body"]["body"]
        note_id = note_body["id"]
        note_text = note_body["text"]
        if note_text is None:
            note_text = ""

        if self.need():  # 100回受信したならメッセージを送信
            self.logger.info("Sended message to avoid Websocket disconnection")
            ws.send("this is dummy message")

        # Renote不可ならreturn
        return_flg = True
        if self.ngw.match(note_text):
            self.logger.info(f"Detected NG word. | noteId: {note_id}, \
                               word: {self.ngw.why(note_text)}")
        elif misskey.can_reply(note_body):
            Thread(target=misskey.reply, args=(note_id, "Pong!")).start()
        elif not misskey.can_renote(note_body):
            pass
        elif note_body["userId"] in set(self.db):
            self.logger.debug("Skiped api request because it was registered in DB.")
        else:
            return_flg = False

        if return_flg:
            return None

        self.logger.debug(
            f"Notes not registered in database. | body: {note_text} , id: {note_id}"
        )
        user_info = misskey.get_user_info(user_id=note_body["userId"])

        if (notes_count := user_info["notesCount"]) == 1:
            self.send_welcome(note_id, note_text)
        elif notes_count <= 10:  # ノート数が10以下ならRenote出来る可能性
            notes = misskey.get_user_notes(note_body["userId"], note_id, 10)
            if all([not misskey.can_renote(note) for note in notes]):
                self.send_welcome(note_id, note_text)
                return None

        if notes_count > 5:
            self.db.append(note_body["userId"])
            if (count := len(self.db)) % 100 == 0:
                utils.update_db("have_note_user_ids", self.db, False)
                self.logger.info(f"DataBase Updated. | length: {count}")

    def on_error(self, ws, error) -> None:
        self.logger.warning(str(error))

    def on_close(self, ws, status_code, msg) -> None:
        self.logger.error(f"WebSocket closed. | code:{status_code} msg: {msg}")
        if self._restart:
            self.start_bot()

    def start_bot(self):
        streaming_api = f"wss://{misskey.HOST}/streaming?i={misskey.TOKEN}"
        USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"  # NOQA
        MESSAGE = {"type": "connect", "body": {"channel": "hybridTimeline", "id": "1"}}
        # WebSocketの接続
        ws = websocket.WebSocketApp(
            streaming_api,
            on_message=self.on_message, on_error=self.on_error, on_close=self.on_close,
            header={"User-Agent": USER_AGENT}
        )
        ws.on_open = lambda ws: ws.send(json.dumps(MESSAGE))
        self.logger.info("Bot was started!")
        ws.run_forever()
