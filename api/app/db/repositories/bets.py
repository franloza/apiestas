import calendar

from motor.motor_asyncio import AsyncIOMotorDatabase
from slugify import slugify

from ...db.errors import EntityDoesNotExist
from ...db.repositories.base import BaseRepository
from ...core.config import COLLECTION_NAME
from ...models.bets import BetBase, BetInDB, BetInUpsert, Bet
from ...models.matches import MatchInDB, MatchBase


class BetsRepository(BaseRepository):
    def __init__(self, client: AsyncIOMotorDatabase) -> None:
        super().__init__(client)
        self._client = self._client[COLLECTION_NAME]

    async def get_bet_by_slug(self, slug: str) -> BetInDB:
        doc = await self.client.find_one({'bets.slug':slug}, {'_id': 0, 'bets.$': 1})
        if doc:
            return BetInDB(**doc["bets"][0])
        else:
            raise EntityDoesNotExist("bet with slug {0} does not exist".format(slug))

    async def upsert_bet(self, match: MatchInDB, bet: BetInUpsert) -> Bet:
        match_bets_aux = {match_bet.slug: match_bet for match_bet in match.bets}
        bet_slug = self.get_bet_slug(match, bet)
        if bet_slug in match_bets_aux:
            # Update bet
            db_bet = BetInDB(**bet.dict(), slug=bet_slug, created_at=match_bets_aux[bet_slug].created_at)
            db_bet_dict = db_bet.dict()
            self.client.update_one(
                {'slug': match.slug, 'bets.slug': bet_slug},
                {'$set': {'bets.$': db_bet_dict}}
            )
        else:
            # Insert bet
            db_bet = BetInDB(**bet.dict(), slug=bet_slug)
            db_bet_dict = db_bet.dict()
            self.client.update_one(
                {'slug': match.slug},
                {'$push': {'bets': db_bet_dict}}
            )
        return Bet(**db_bet_dict)

    @staticmethod
    def get_bet_slug(match: MatchBase, bet: BetBase) -> str:
        return slugify(','.join
                       (match.teams + list(map(str, (match.sport, match.tournament,
                                                     calendar.timegm(match.commence_time.utctimetuple()),
                                                     bet.bookmaker, bet.bet_type, bet.bet_scope)))))


