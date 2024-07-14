import logging_styles

logger = logging_styles.getLogger(__name__)


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


def can_reply(note: dict, username: str) -> bool:
    """リプライ可能(pingノート)か判定

    Args:
        note (dict): misskeyのノート

    Returns:
        bool: リプライ可能か
    """
    if note["text"] is None:
        return False
    is_ping = "/ping" in note["text"]
    is_mention = f"@{username}" in note["text"]
    is_specified = note["visibility"] == "specified"
    return is_ping and (is_mention or is_specified)
