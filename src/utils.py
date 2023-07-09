import time
import os
import pickle
from typing import Any
from collections import deque

import dotenv


class RateLimiter:
    def __init__(self, per_second: int):
        """レートリミット

        Args:
            per_second (int): 1回の間隔
        """
        self.per_second = per_second  # リクエスト送信の間隔（秒）
        self.last_called_time = time.time()

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            self.wait()
            response = func(*args, **kwargs)
            self.last_called_time = time.time()
            return response
        return wrapper

    def wait(self):
        elapsed_time = time.time() - self.last_called_time
        if elapsed_time < self.per_second:
            time.sleep(self.per_second - elapsed_time)


class Counter:
    def __init__(self, counter, do) -> None:
        self.count = counter
        self._now = 0
        self.do = do

    def __call__(self, f) -> Any:
        def wrapper(*args, **kwargs):
            self._now += 1
            if self._now == self.count:
                self._now = 0
                self.do()

            resp = f(*args, **kwargs)
            return resp
        return wrapper


def config_dir():
    dotenv.load_dotenv()
    dir = os.getenv("CONFIG_DIR", "./config")
    if not os.path.exists(dir):
        raise FileNotFoundError("Config directory not found.")
    return dir


def db_type():
    dotenv.load_dotenv()
    return os.getenv("DB_TYPE")


def update_db(key: str, value, allow_duplicates: bool = True) -> None:
    if not allow_duplicates:
        value = set(value)

    if db_type() == "redis":
        import redis
        dotenv.load_dotenv()

        r = redis.from_url(os.getenv("DB_URL"))
        r.sadd("have_note_user_ids", *value)
    elif db_type() == "pickle":
        with open("./data/users.pickle", "wb") as f:
            pickle.dump(deque(value), f)


def get_db():
    if db_type() == "redis":
        import redis
        dotenv.load_dotenv()

        r = redis.from_url(os.getenv("DB_URL"))
        return deque(map(lambda x: x.decode(), r.smembers("have_note_user_ids")))
    elif db_type() == "pickle":
        try:
            with open('./data/users.pickle', "rb") as f:
                have_note_user_ids = pickle.load(f)
        except FileNotFoundError:
            have_note_user_ids = deque()
        return have_note_user_ids
