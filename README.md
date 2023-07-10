<div align="center">

## Misskey-WelcomeBot
<img src="https://s3.arkjp.net/misskey/webpublic-1c253796-7dc4-4d54-8367-ad2259693ce7.png" height="125" alt="Logo" />

---
MisskeyのようこそBotのリポジトリです。
</div>

~~注意:これはReplitでの動作を想定しています。replit以外で動作させる場合は(branch name)を使用してください。~~
replitはダウンタイムが多すぎるので切り捨てました()

## 何のBot?
ローカルタイムライン(TL)に流れてきた初ノートにリアクションをつけたりリノートします。
(APIへのリクエストを削減するために、DB(redis)にユーザーIDを保存しています。)

条件
- 投稿したユーザーのノート数が1(初ノート)
- NGワードが含まれていない
<br /><br />

## 設定
1. `sample.env`の名前を`.env`に変更し、中を編集します。
```dotenv
HOST=misskey.io  # host
SECRET_TOKEN=token  # misskeyのtoken
CONFIG_DIR=./config  # configフォルダを指定
RUN_SERVER=False  # サーバーを建てるならTrue
DB_TYPE=redis  # redisかpickleで指定
DB_URL=redis://dw  # redisならurlを入力(pickleなら不要)
```

2. response.jsonの編集

このファイルはconfigディレクトリに保存してください。
`keywords`にトリガーとなるキーワードを**配列**で指定してください。

`emoji`に反応する絵文字の一覧を指定してください。ここは配列か文字列にしてください。配列の場合はランダムで選択します。
otherにはトリガーにあてはまらなかった場合の絵文字を指定してください。
例：
```json
{
    "triggers": [
        {
            "keywords": ["レターパック", ":5000", "れたはす"],
            "emoji": ":send_money:"
        },
        {
            "keywords": ["与謝野晶子"],
            "emoji": [
                ":yosano_akiko_is_always_watching_you:",
                ":yosano_akiko:",
                ":yosano_party:",
                ":petthex_yosano_akiko:",
                ":youseino_akiko:"
            ]
        }
    ],
    "others": [
        ":youkoso:",
        ":youkoso_send_money:",
        ":send_money:",
        ":welcome_to_underground:",
        ":supertada:",
    ]
}
```

3. NGワードの設定

configディレクトリにngwords.txtを作成します。
NGワードを記述します。

書式
- 除外するワードは-をつけてから書きます(スペースはつけない)
- #から始めるとコメントになります。

4. keep_alive.pyを起動
