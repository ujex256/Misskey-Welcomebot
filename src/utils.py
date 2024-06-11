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
