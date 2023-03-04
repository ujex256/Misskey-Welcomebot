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
TOKEN = os.environ["MISSKEY-TOKEN"]

def on_message(ws, message):
    note_body = json.loads(message)["body"]["body"]
    note_id = note_body["id"]
    if not (note_body["text"] == None):
        print(note_body["text"])
    user_info = requests.post(
        "https://misskey.io/api/users/show",
        json={
            "username": note_body["user"]["username"],
            "i": TOKEN,
        },
    )
    print(user_info.json()["notesCount"], user_info.json()["notesCount"] == 1)
    if user_info.json()["notesCount"] == 1:
        requests.post(
            "https://misskey.io/api/notes/reactions/create",
            json={
                "noteId": note_id,
                "reaction": random.choice(WELCOME_REACTIONS),
                "i": TOKEN,
            },
        )
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
