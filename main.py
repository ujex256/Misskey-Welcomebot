import websocket
import requests
import json
import random
import os


WELCOME_REACTIONS = [
    ":youkoso:",
    ":youkoso_send_money:",
    ":send_money:",
    ":nyanpuppu:",
    ":supertada:",
    ":blob_hello:",
]
TOKEN = os.environ["MISSKEY-ACCESSTOKEN"]
with open("ngwords.txt", "r", encoding="utf8") as f:
    words = f.read()
    NG_WORDS = [i for i in words.split("\n") if (i[0] != "-") and (i[0] != "#")]
    EXCLUDED_WORDS = [i[1:] for i in words.split("\n") if i[0] == "-"]

def on_message(ws, message):
    note_body = json.loads(message)["body"]["body"]
    note_id = note_body["id"]
    note_text = note_body["text"]

    # 脳筋コード
    for i in NG_WORDS:
        flag = False
        if i in note_text:
            for j in EXCLUDED_WORDS:
                if j in note_text:
                    flag = True
                    break
            if not flag:
                return
    if not (note_text == None):
        print(note_text)
        user_info = requests.post(
            "https://misskey.io/api/users/show",
            json={
                "username": note_body["user"]["username"],
                "i": TOKEN,
            },
        )
        if user_info.json()["notesCount"] == 1:
            if "レターパック" in note_text or ":5000" in note_text:
                reaction = ":send_money:"
            else:
                reaction = random.choice(WELCOME_REACTIONS)
            print(f"[Reaction Added] noteId>>{note_id}, reaction>>{reaction}")
            requests.post(
                "https://misskey.io/api/notes/reactions/create",
                json={
                    "noteId": note_id,
                    "reaction": reaction,
                    "i": TOKEN,
                },
            )
            print("[Renote] noteId", note_id)
            requests.post(
                "https://misskey.io/api/notes/create",
                json={
                    "localOnly": True,
                    "renoteId": note_id,
                    "i": TOKEN,
                },
            )

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("WebSocket closed")

if __name__ == "__main__":
    streaming_api = f"wss://misskey.io/streaming?i={TOKEN}"
    # WebSocketの接続
    ws = websocket.WebSocketApp(streaming_api, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = lambda ws: ws.send(
        json.dumps({"type": "connect", "body": {"channel": "localTimeline", "id": "1"}})
    )
    ws.run_forever()
