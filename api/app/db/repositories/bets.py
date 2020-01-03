from datetime import datetime
from time import mktime

from motor.motor_asyncio import AsyncIOMotorDatabase
from slugify import slugify

from app.db.errors import EntityDoesNotExist
from app.db.repositories.base import BaseRepository

from app.models.bets import BetBase, BetInDB, BetInUpsert, Bet
from app.models.matches import Match, MatchInDB, MatchBase


class BetsRepository(BaseRepository):
    def __init__(self, client: AsyncIOMotorDatabase) -> None:
        super().__init__(client)
        self._client = self._client["matches"]

    async def get_bet_by_slug(self, slug: str) -> BetInDB:
        doc = await self.client.find_one({'bets.slug':slug}, {'_id': 0, 'bets.$': 1})
        if doc:
            return BetInDB(**doc["bets"][0])
        else:
            raise EntityDoesNotExist("bet with slug {0} does not exist".format(slug))

    async def upsert_bet(self, match: MatchInDB, bet: BetInUpsert) -> Bet:
        bets = list(map(lambda x: x.dict(), match.bets))
        slug = self.get_bet_slug(match, bet)
        db_bet, db_bet_idx = None, -1
        for idx, match_bet in enumerate(match.bets):
            if match_bet.slug == slug:
                db_bet = match_bet
                db_bet_idx = idx
        if db_bet:
            # Update bet
            db_bet.url = bet.url
            db_bet.odds = bet.odds
            db_bet.updated_at = datetime.utcnow().replace(microsecond=0)
            db_bet_dict = db_bet.dict()
            bets[db_bet_idx] = db_bet_dict
        else:
            # Insert bet
            db_dict = bet.dict()
            db_dict["slug"] = slug
            db_bet = BetInDB(**db_dict)
            db_bet_dict = db_bet.dict()
            bets.append(db_bet_dict)
        await self.client.update_one({'slug': match.slug}, {'$set': {'bets': bets}})
        return Bet(**db_bet_dict)

    @staticmethod
    def get_bet_slug(match: MatchBase, bet: BetBase) -> str:
        return slugify(','.join
                       (match.teams + list(map(str, (match.sport, match.tournament,
                                                     int(mktime(match.commence_time.timetuple())), bet.bookmaker)))))


