from time import mktime

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from slugify import slugify

from app.db.errors import EntityDoesNotExist
from app.db.repositories.base import BaseRepository
from app.models.bets import BetBase
from app.models.matches import Match, MatchInUpsert, MatchBase


class BetsRepository(BaseRepository):
    def __init__(self, client: AsyncIOMotorDatabase) -> None:
        super().__init__(client)
        self._client = self._client["matches"]

    async def get_bet_slug(self, match: MatchBase, bet: BetBase) -> str:
        return slugify(' '.join(match.teams + [match.sport, match.tournament, mktime(match.commence_time.timetuple()),
                                       bet.bookmaker]))


