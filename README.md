<div align="center">

## Misskey-WelcomeBot
<img src="https://s3.arkjp.net/misskey/webpublic-1c253796-7dc4-4d54-8367-ad2259693ce7.png" height="125" alt="Logo" />

---
MisskeyのようこそBotのリポジトリです。
</div>

**注意:これはReplitでの動作を想定しています。Replit以外で動作させる場合は[no-replitブランチ](https://github.com/ujex256/Misskey-Welcomebot/tree/no-replit)を使用してください。**

## 何のBot?
ローカルタイムライン(TL)に流れてきた初ノートにリアクションをつけたりリノートします。

条件
- 投稿したユーザーのノート数が1(初ノート)
- NGワードが含まれていない


APIへのリクエストを削減するために、ReplitのDBにユーザーIDを保存しています。
Replitを使用しない場合は、dataディレクトリの中に`users.pickle`というファイルが作成され、そこに保存されます。
<br /><br />

## 設定
1. `sample.env`の名前を`.env`に変更し、中を編集します。
```sh
HOST=misskey.io
SECRET-TOKEN=token
```
2. response.jsonの編集
`keywords`にトリガーとなるキーワードを**配列**で指定してください。

`emoji`に反応する絵文字の一覧を指定してください。ここは配列か文字列にしてください。配列の場合はランダムで選択します。
```json
[
    {
        "keywords": ["レターパック"],
        "emoji": ":send_money:"
    },
    {
        "keywords": ["yosano", "与謝野晶子"],
        "emoji": [
            ":yosano_akiko_is_always_watching_you:",
            ":yosano_akiko:",
            ":yosano_party:",
        ]
    },
]
```
## クレジット
ようこそBotのアイコン: [**@nullkal**](https://misskey.io/notes/9bhuk9wlo9)