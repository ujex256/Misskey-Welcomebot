import asyncio
import json
from threading import Thread

import websockets

import utils
import logging_styles
import misskey_api as misskey
from environs import Settings
from userdb import UserDB
from ngwords import NGWords
from emojis import EmojiSet


class Bot:
    counter = utils.Counter(100, lambda: None)

    def __init__(self, settings: Settings, restart: bool = True) -> None:
        self.logger = logging_styles.getLogger(__name__)
        self.config = settings
        self._restart = restart

        self.config_dir = self.config.config_dir

        self.logger.info("Loading response.json...")
        self.emojis = EmojiSet(str(self.config_dir.joinpath("response.json")))
        self.logger.info("Loading ngwords.txt...")
        self.ngw = NGWords(str(self.config_dir.joinpath("ngwords.txt")))

        self.db = UserDB(str(self.config.db_url))  # TODO: redis以外への対応

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

    async def on_message(self, ws, message: str) -> None:
        note_body = json.loads(message)["body"]["body"]
        note_id = note_body["id"]
        note_text = note_body["text"]
        user_id = note_body["userId"]
        if note_text is None:
            note_text = ""

        if self.need():  # 100回受信したならメッセージを送信
            self.logger.info("Sended message to avoid Websocket disconnection")
            ws.send("this is dummy message")

        # Renote不可ならreturn
        return_flg = True
        if self.ngw.match(note_text):
            self.logger.info(
                f"Detected NG word. | noteId: {note_id}, \
                               word: {self.ngw.why(note_text)}"
            )
        elif misskey.can_reply(note_body):
            Thread(target=misskey.reply, args=(note_id, "Pong!")).start()
        elif not misskey.can_renote(note_body):
            pass
        elif await self.db.get_user_by_id(user_id):
            self.logger.debug("Skiped api request because it was registered in DB.")
        else:
            return_flg = False

        if return_flg:
            return None

        self.logger.debug(
            f"Notes not registered in database. | body: {note_text} , id: {note_id}"
        )
        user_info = misskey.get_user_info(user_id=user_id)

        if (notes_count := user_info["notesCount"]) == 1:
            self.send_welcome(note_id, note_text)
        elif notes_count <= 10:  # ノート数が10以下ならRenote出来る可能性
            notes = misskey.get_user_notes(user_id, note_id, 10)
            if all([not misskey.can_renote(note) for note in notes]):
                self.send_welcome(note_id, note_text)
                return None

        if notes_count > 5:
            await self.db.add_user(user_id, note_body["user"]["username"])
            self.logger.info("DataBase Updated.")

    async def on_error(self, ws, error) -> None:
        self.logger.warning(str(error))

    async def on_close(self, ws, status_code, msg) -> bool:
        self.logger.error(f"WebSocket closed. | code:{status_code} msg: {msg}")
        return self._restart

    async def start_bot(self):
        streaming_api = f"wss://{misskey.HOST}/streaming?i={misskey.TOKEN}"
        USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"  # NOQA
        CONNECTMSG = {
            "type": "connect",
            "body": {"channel": "hybridTimeline", "id": "1"},
        }

        while True:
            async with websockets.connect(streaming_api, user_agent_header=USER_AGENT) as ws:
                # self.on_open(ws)
                self.logger.info("Bot was started!")
                await ws.send(json.dumps(CONNECTMSG))
                while True:
                    try:
                        msg = await ws.recv()
                        await self.on_message(ws, str(msg))
                    except websockets.ConnectionClosed:
                        await self.on_close(ws, ws.close_code, ws.close_reason)
                        if not self._restart:
                            return
                        break
                    except Exception as e:
                        await self.on_error(ws, e)
            await asyncio.sleep(5)
