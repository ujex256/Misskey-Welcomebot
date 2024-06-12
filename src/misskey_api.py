from os import getenv

import requests
from dotenv import load_dotenv
from requests import Timeout

import logging_styles
from utils import RateLimiter


load_dotenv()
HOST = getenv("HOST").replace("https://", "")
TOKEN = getenv("SECRET_TOKEN")
USERNAME = requests.post(f"https://{HOST}/api/i", json={"i": TOKEN}).json()["username"]

logger = logging_styles.getLogger(__name__)

limiter = RateLimiter(0.5)
limiter2 = RateLimiter(0.5)
TIMEOUT_SEC = 5


def renote(note_id: str) -> None:
    try:
        resp = requests.post(
            f"https://{HOST}/api/notes/create",
            json={
                "localOnly": True,
                "renoteId": note_id,
                "i": TOKEN,
            },
            timeout=TIMEOUT_SEC
        )
    except Timeout:
        logger.warning("API timed out. | endpoint: notes/create")
    if resp.ok:
        logger.info(f"Renoted! noteId: {note_id}")
    else:
        logger.error(f"Renote failed noteId: {note_id}, msg: {resp.text}")


def add_reaction(note_id: str, reaction: str) -> None:
    try:
        resp = requests.post(
            f"https://{HOST}/api/notes/reactions/create",
            json={
                "noteId": note_id,
                "reaction": reaction,
                "i": TOKEN,
            },
            timeout=TIMEOUT_SEC
        )
    except Timeout:
        logger.warning("API timed out. | endpoint: notes/reactions/create")
        return None
    if resp.ok:
        logger.info(f"Reaction added noteId: {note_id}, reaction: {reaction}")
    else:
        logger.error(f"Failed to add reaction. | noteId: {note_id}, msg: {resp.text}")


def reply(note_id: str, msg: str):
    try:
        resp = requests.post(
            f"https://{HOST}/api/notes/create",
            json={
                "localOnly": True,
                "text": msg,
                "replyId": note_id,
                "i": TOKEN,
            },
            timeout=TIMEOUT_SEC
        )
    except Timeout:
        logger.warning("API timed out. | endpoint: notes/create")
        return None
    if resp.ok:
        logger.info(f"Replied! noteId: {note_id}, msg: {msg}")
    else:
        logger.error(f"Reply failed. | noteId: {note_id}, msg: {resp.text}")


@limiter
def get_user_info(user_name: str = "", user_id: str = "") -> dict | None:
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
        resp = requests.post(
            f"https://{HOST}/api/users/show",
            json=body,
            timeout=TIMEOUT_SEC,
        )
    except Timeout:
        logger.warning("API timed out. | endpoint: users/show")
        return None
    if resp.ok:
        return resp.json()


@limiter2
def get_user_notes(user_id: str, until_id: str, limit: int):
    try:
        body = {
            "userId": user_id,
            "untilId": until_id,
            "limit": limit,
            "i": TOKEN,
        }
        resp = requests.post(
            f"https://{HOST}/api/users/notes",
            json=body,
            timeout=TIMEOUT_SEC,
        )
    except Timeout:
        logger.warning("API timed out. | endpoint: users/notes")
        return None
    if resp.ok:
        return resp.json()


def can_renote(note: dict) -> bool:
    """リノート可能か判定する(ノート数はカウントしていないので注意)

    Args:
        note (dict): misskeyのノート

    Returns:
        bool: 可能か
    """
    is_public = note["visibility"] == "public"
    text_exists = note["text"] is not None
    is_reply = note["replyId"] is not None
    return is_public and text_exists and not is_reply


def can_reply(note: dict) -> bool:
    """リプライ可能(pingノート)か判定

    Args:
        note (dict): misskeyのノート

    Returns:
        bool: リプライ可能か
    """
    if note["text"] is None:
        return False
    is_ping = "/ping" in note["text"]
    is_mention = f"@{USERNAME}" in note["text"]
    is_specified = note["visibility"] == "specified"
    return is_ping and (is_mention or is_specified)
