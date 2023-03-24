import time


class RateLimiter:
    def __init__(self, per_second: int):
        """レートリミット

        Args:
            per_second (int): 1秒あたり何回か
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
