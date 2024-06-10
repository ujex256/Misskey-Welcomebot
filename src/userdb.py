import asyncio

from pydantic import PastDatetime
from aredis_om import HashModel, get_redis_connection, Field

from datetime import datetime


class UserInfo(HashModel):
    user_id: str = Field(primary_key=True)
    user_name: str
    last_received_date: PastDatetime

    class Meta:
        global_key_prefix = "MisskeyWelcomeBot"
        model_key_prefix = "PostedUsers"


class UserDB:
    def __init__(self, redis_url: str) -> None:
        self._db_url = redis_url
        UserInfo.Meta.database = get_redis_connection(url=self._db_url, decode_responses=True)  # type: ignore

    async def get_all_users(self) -> list[UserInfo]:
        all_pks = await UserInfo.all_pks()
        return await asyncio.gather(*[UserInfo.get(i) async for i in all_pks])

    async def get_user(self, user_id: str) -> UserInfo:
        return await UserInfo.get(user_id)

    async def add_user(self, user_id: str, username: str):
        await UserInfo(
            user_id=user_id,
            user_name=username,
            last_received_date=datetime.now()
        ).save()


if __name__ == "__main__":
    import asyncio
    from environs import Settings

    db = UserDB(str(Settings().db_url))
    print(asyncio.run(db.get_all_users()))
