import asyncio
from datetime import datetime

from pydantic import PastDatetime
from aredis_om import (
    HashModel,
    Migrator,
    get_redis_connection,
    Field,
    NotFoundError,
)


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

    async def ping(self):
        return await UserInfo.db().ping()

    async def get_all_users(self) -> list[UserInfo]:
        all_pks = await UserInfo.all_pks()
        return await asyncio.gather(*[UserInfo.get(i) async for i in all_pks])

    async def get_user_by_id(self, id: str) -> UserInfo | None:
        try:
            return await UserInfo.get(id)
        except NotFoundError:
            return None

    async def get_user_by_name(self, name: str) -> UserInfo | None:
        await self._migrate()
        found = UserInfo.find(UserInfo.user_name == name)
        try:
            return await found.first()  # type: ignore
        except NotFoundError:
            return None

    async def add_user(self, user_id: str, username: str) -> None:
        await UserInfo(
            user_id=user_id,
            user_name=username,
            last_received_date=datetime.now(),
        ).save()

    async def _migrate(self) -> None:
        await Migrator().run()


if __name__ == "__main__":
    import asyncio, environs

    db_url = environs.Settings().db_url
    if db_url is None:
        exit(print("db_type is not redis"))
    db = UserDB(str(db_url))
    print(asyncio.run(db.get_user_by_name("ffdi")))
