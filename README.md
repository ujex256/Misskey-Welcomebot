# Misskey-WelcomeBot
<div align="center">

<img src="https://s3.arkjp.net/misskey/webpublic-1c253796-7dc4-4d54-8367-ad2259693ce7.png" height="125" alt="Logo" />

---
MisskeyのようこそBotのリポジトリです。
</div>

## 何のBot?
タイムラインに流れてきた新規ユーザーのノートにリアクションをつけたり、リノートします。

条件
- 投稿したユーザーの合計ノート数が1である（初投稿）
- NGワードが含まれていない
<br /><br />

## 設定
### 1. `env.example`の名前を`.env`に変更し、中を編集します
```dotenv
HOST=misskey.example.com  # Misskeyのホスト(misskey.ioなど)
SECRET_TOKEN=token  # Misskeyのtoken
DB_TYPE=redis
DB_URL=redis://dw  # RedisのURLを入力
```

環境変数一覧
| 変数名 | 型 | 必須 | 内容 | デフォルト |
|---|---|:---:|---|---|
| HOST | str | :heavy_check_mark: | Misskeyのホスト |  |
| SECRET_TOKEN | str | :heavy_check_mark: |  |  |
| DB_TYPE | str |  | 投稿したことがあるユーザーをキャッシュさせるDBの種類<br />(今はredisのみ) | redis |
| DB_URL | str(RedisDsn) |  | DB_TYPEがredisの場合に指定してください |  |
| RUN_SERVER | bool |  | pingサーバーを起動するか(UptimeRobotなどの監視用) | false |
| SERVER_HOST | str(IPvAnyAddress) |  | pingサーバーを起動するホスト | 0.0.0.0 |
| SERVER_PORT | str |  | pingサーバーを起動するポート | 8000 |
| CONFIG_DIR | str(directory path) |  | configディレクトリを変更する場合のパス | ./config |



### 2. response.jsonの編集

このファイルはconfigディレクトリに保存してください。
`keywords`にトリガーとなるキーワードを**配列**で指定してください。

`emoji`に反応する絵文字の一覧を配列か文字列で指定してください。配列の場合はランダムで選択されます。

トリガーにあてはまらなかった場合は`other`に指定された絵文字がランダムで選択されます。

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
                ":yosano_akiko:"
            ]
        }
    ],
    "others": [
        ":youkoso:",
        ":youkoso_send_money:",
        ":send_money:",
        ":welcome_to_underground:",
        ":supertada:"
    ]
}
```

### 3. NGワードの設定

configディレクトリにngwords.txtを作成します。
NGワードを記述します。

書式
- 除外するワードは-をつけてから書きます（スペースをつけてもOK）
- #から始めるとコメントになります。

### 4. keep_alive.pyを起動
```sh
python src/keep_alive.py
```
