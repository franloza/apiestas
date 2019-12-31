from typing import AsyncGenerator, Callable, Type

from fastapi import Depends
from starlette.requests import Request


from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import config
from app.db.repositories.base import BaseRepository


def _get_db_client(request: Request) -> AsyncIOMotorClient:
    return request.app.state.db


def get_repository(repo_type: Type[BaseRepository]) -> Callable:  # type: ignore
    async def _get_repo(
        client: AsyncIOMotorClient = Depends(_get_db_client),
    ) -> AsyncGenerator[BaseRepository, None]:
        yield repo_type(client[config.MONGO_DB])
    return _get_repo