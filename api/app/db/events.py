from fastapi import FastAPI
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import DATABASE_URL, MAX_CONNECTIONS_COUNT, MIN_CONNECTIONS_COUNT


async def connect_to_db(app: FastAPI) -> None:
    logger.info(f"Connecting to {repr(DATABASE_URL)}")
    app.state.db = AsyncIOMotorClient(
        str(DATABASE_URL),
        maxPoolSize=MAX_CONNECTIONS_COUNT,
        minPoolSize=MIN_CONNECTIONS_COUNT)
    logger.debug(await app.state.db.server_info())
    logger.info("Connection established")


async def close_db_connection(app: FastAPI) -> None:
    logger.info("Closing connection to database")
    await app.state.db.close()
    logger.info("Connection closed")