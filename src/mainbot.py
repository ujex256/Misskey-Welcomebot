import asyncio
import json
import traceback

import websockets
from aiohttp import ClientSession
from asynciolimiter import Limiter
from misskey.asynchronous import AsyncMisskey
from marshmallow.exceptions import ValidationError

import utils
import logging_styles
import misskey_api as misskey
from environs import Settings
from userdb import UserDB
from ngwords import NGWords
from emojis import EmojiSet


class Bot:
    counter = utils.Counter(100, lambda: None)

    def __init__(
        self,
        settings: Settings,
        aiosession: ClientSession,
        restart: bool = True
    ) -> None:
        self.logger = logging_styles.getLogger(__name__)
        self.config = settings
        self._restart = restart

        conf = self.config.config_dir

        self.logger.info("Loading response.json...")
        self.emojis = EmojiSet(str(conf.joinpath("response.json")))
        self.logger.info("Loading ngwords.txt...")
        self.ngw = NGWords(str(conf.joinpath("ngwords.txt")))

        self._api_session = aiosession
        self.api = AsyncMisskey(
            address=self.config.host,
            token=self.config.secret_token,
            session=self._api_session
        )
        self.db = UserDB(str(self.config.db_url))  # TODO: redis以外への対応
        self.limiter = Limiter(3)
        self.limiter2 = Limiter(3)
        self.me = ""

    async def send_welcome(self, note_id: str, note_text: str) -> None:
        """Send welcome message.

        Args:
            note_id (str): note id
            note_text (str): note text
        """
        reaction = self.emojis.get_response_emoji(note_text)
        await self.api._api_request(
            endpoint="/api/notes/reactions/create",
            params={"noteId": note_id, "reaction": reaction}
        )
        await self.api.notes_create(renote_id=note_id, local_only=True)
        self.logger.info(f"Sent welcome message | id: {note_id}, reaction: {reaction}")

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
            await ws.send("this is dummy message")

        # Renote不可ならreturn
        return_flg = True
        if self.ngw.match(note_text):
            self.logger.info(
                f"Detected NG word. | noteId: {note_id}, "
                f"word: {self.ngw.why(note_text)}"
            )
        elif misskey.can_reply(note_body, self.me):
            await self.api.notes_create(text="Pong!", reply_id=note_id, local_only=True)
        elif not misskey.can_renote(note_body):
            pass
        elif await self.db.get_user_by_id(user_id):
            self.logger.debug("Skipped api request because it was registered in DB.")
        else:
            return_flg = False

        if return_flg:
            return None

        self.logger.debug(
            f"Notes not registered in database. | userId: {user_id}, noteId: {note_id}"
        )
        await self.limiter.wait()
        user_info = await self.api._api_request(
            endpoint="/api/users/show",
            params={"userId": user_id}
        )

        if (notes_count := user_info["notesCount"]) == 1:
            await self.send_welcome(note_id, note_text)
        elif notes_count <= 10:  # ノート数が10以下ならRenote出来る可能性
            body = {
                "userId": user_id,
                "untilId": note_id,
                "limit": 10,
            }
            try:
                await self.limiter2.wait()
                notes = await self.api._api_request(endpoint="/api/users/notes", params=body)
            except asyncio.TimeoutError:
                self.logger.warn("API timed out. | endpoint: /api/users/notes")
                return None
            if not any([misskey.can_renote(note) for note in notes]):
                await self.send_welcome(note_id, note_text)
                return None

        if notes_count > 5:
            await self.db.add_user(user_id, note_body["user"]["username"])

    async def on_error(self, ws, error) -> None:
        try:
            raise error
        except asyncio.TimeoutError:
            self.logger.warn("API timed out. | endpoint: Unknown")
        except ValidationError:  # 仮: Misskey.py5.0.0a1
            pass
        except Exception:
            msg = traceback.format_exc()
            self.logger.error(msg)

    async def on_close(self, ws, status_code, msg) -> bool:
        self.logger.error(f"WebSocket closed. | code:{status_code} msg: {msg}")
        return self._restart

    async def start_bot(self):
        me = await self.api.i()
        self.me = me.username
        self.logger.info(f"User name: {self.me}")

        streaming_api = f"wss://{self.config.host}/streaming?i={self.config.secret_token}"
        USER_AGENT = "Misskey-Welcomebot (repo: https://github.com/ujex256/Misskey-Welcomebot)"  # NOQA
        CONNECTMSG = {
            "type": "connect",
            "body": {"channel": "hybridTimeline", "id": "1"},
        }

        pong = await self.db.ping()
        if not pong:
            raise Exception("DB connection failed.")

        while True:
            async with websockets.connect(streaming_api, user_agent_header=USER_AGENT) as ws:
                # self.on_open(ws)
                self.logger.info("Bot was started!")
                await ws.send(json.dumps(CONNECTMSG))
                while True:
                    try:
                        msg = await ws.recv()
                        tsk = asyncio.create_task(self.on_message(ws, str(msg)))
                        await tsk
                    except websockets.ConnectionClosed:
                        await self.on_close(ws, ws.close_code, ws.close_reason)
                        if not self._restart:
                            return
                        break
                    except Exception as e:
                        await self.on_error(ws, e)
            await asyncio.sleep(5)
