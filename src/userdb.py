import asyncio

from pydantic import PastDatetime
from aredis_om import HashModel, Migrator, get_redis_connection, Field, NotFoundError

from datetime import datetime


class UserInfo(HashModel):
    user_id: str = Field(primary_key=True)
    user_name: str = Field(index=True)
    last_received_date: PastDatetime

    class Meta:
        global_key_prefix = "MisskeyWelcomeBot"
        model_key_prefix = "PostedUsers"


class UserDB:
    def __init__(self, redis_url: str) -> None:
        self._db_url = redis_url
        UserInfo.Meta.database = get_redis_connection(url=self._db_url)  # type: ignore

    async def get_all_users(self) -> list[UserInfo]:
        all_pks = await UserInfo.all_pks()
        return await asyncio.gather(*[UserInfo.get(i) async for i in all_pks])

    async def get_user_by_id(self, user_id: str) -> UserInfo | None:
        try:
            return await UserInfo.get(user_id)
        except NotFoundError:
            return None

    async def get_user_by_name(self, aas: str) -> UserInfo | None:
        await self._migrate()
        a = UserInfo.find(UserInfo.user_name == aas)
        try:
            return await a.first()  # type: ignore
        except NotFoundError:
            return None

    async def add_user(self, user_id: str, username: str) -> None:
        await UserInfo(
            user_id=user_id, user_name=username, last_received_date=datetime.now()
        ).save()

    async def _migrate(self) -> None:
        await Migrator().run()


if __name__ == "__main__":
    import asyncio

    DB_URL = "redis://localhost:6379"
    db = UserDB(DB_URL)
    print(type(asyncio.run(db.get_user_by_name("ffdi"))))
