from motor.motor_asyncio import AsyncIOMotorDatabase


class BaseRepository:
    def __init__(self, client: AsyncIOMotorDatabase) -> None:
        self._client = client

    @property
    def client(self) -> AsyncIOMotorDatabase:
        return self._client
