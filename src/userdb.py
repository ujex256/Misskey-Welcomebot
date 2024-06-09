from redis_om import HashModel, get_redis_connection
from pydantic import PastDatetime


class UserInfo(HashModel):
    user_name: str
    last_recieved_date: PastDatetime
