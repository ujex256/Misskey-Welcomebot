import pickle
import logging
import logging.config
from os import getenv
from collections import deque

import requests
import coloredlogs
from dotenv import load_dotenv
from requests import Timeout


load_dotenv()
HOST = getenv("HOST")
TOKEN = getenv("SECRET-TOKEN")

logger = logging.getLogger(__name__)
coloredlogs.install(logger=logger)

def renote(note_id: str) -> None:
    res = requests.post(
        f"https://{HOST}/api/notes/create",
        json={
            "localOnly": True,
            "renoteId": note_id,
            "i": TOKEN,
        },
    )
    if res.ok:
        logger.info(f"Renoted! noteId: {note_id}")
    else:
        logger.error(f"Renote failed noteId: {note_id}, msg: {res.text}")

def add_reaction(note_id: str, reaction: str) -> None:
    res = requests.post(
        f"https://{HOST}/api/notes/reactions/create",
        json={
            "noteId": note_id,
            "reaction": reaction,
            "i": TOKEN,
        },
    )
    if res.ok:
        logger.info(f"Reaction added noteId: {note_id}, reaction: {reaction}")
    else:
        logger.error(f"Failed to add reaction noteId: {note_id}, msg: {res.text}")

def get_user_info(user_name: str="", user_id: str="") -> dict | None:
    if user_name and user_id:
        raise Exception("どっちかにして")
    try:
        body = {
            "username": user_name,
            "userId": user_id,
            "i": TOKEN,
        }
        if user_id:
            body.pop("username")
        else:
            body.pop("userId")
        user_info = requests.post(
            f"https://{HOST}/api/users/show",
            json=body, timeout=5,
        )
        return user_info.json()
    except Timeout:
        logger.warning("api timeout")

def reply(note_id: str, msg: str):
    res = requests.post(
        f"https://{HOST}/api/notes/create",
        json={
            "localOnly": True,
            "text": msg,
            "replyId": note_id,
            "i": TOKEN,
        },
    )
    if res.ok:
        logger.info(f"Replied! noteId: {note_id}, msg: {msg}")
    else:
        logger.error(f"Reply failed noteId: {note_id}, msg: {res.text}")


# Misskeyに関係ない
def update_db(key: str, value, allow_duplicates: bool=True) -> None:
    if not allow_duplicates and isinstance(value, deque):
        value = deque(set(value))
    with open("./data/users.pickle", "wb") as f:
        pickle.dump(value, f)