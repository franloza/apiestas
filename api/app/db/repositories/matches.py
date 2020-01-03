from collections import OrderedDict
from datetime import datetime, timedelta, date
from time import mktime
from typing import List

from motor.motor_asyncio import AsyncIOMotorDatabase
from slugify import slugify

from app.db.errors import EntityDoesNotExist
from app.db.repositories.base import BaseRepository
from app.db.repositories.bets import BetsRepository

from app.models.bets import BetInDB
from app.models.matches import Match, MatchInUpsert, MatchBase, MatchInDB


class MatchesRepository(BaseRepository):
    def __init__(self, client: AsyncIOMotorDatabase) -> None:
        super().__init__(client)
        self._client = self._client["matches"]
        self._bets_repository = BetsRepository(client)

    async def get_match_by_slug(self, slug: str) -> MatchInDB:
        doc = await self.client.find_one({"slug": slug})
        if doc:
            return MatchInDB(**doc)
        else:
            raise EntityDoesNotExist("match with slug {0} does not exist".format(slug))

    async def filter_matches(self, commence_day: datetime.date, sport : str, tournament :  str = None,
                             commence_time: datetime.date = None) -> List[Match]:
        query = {"sport": sport}
        if commence_time:
            query["commence_time"] = commence_time
        else:
            commence_time = datetime.combine(commence_day, datetime.min.time())
            query["commence_time"] = {'$gte': commence_time, '$lt': commence_time + timedelta(days=1)}
        if tournament:
            query["tournament"] = tournament
        matches_docs = self.client.find(query)
        return [Match(**match) async for match in matches_docs]

    async def upsert_match(self, match: MatchInUpsert) -> Match:
        slug = self._get_match_slug(match)
        try:
            # Update match
            db_match = await self.get_match_by_slug(slug)
            db_match.feed = match.feed
            db_match_bets_aux = OrderedDict((bet.slug, bet) for bet in db_match.bets)
            for bet in match.bets:
                bet_slug = self._bets_repository.get_bet_slug(match, bet)
                if bet_slug in db_match_bets_aux:
                    db_match_bets_aux[bet_slug].odds = bet.odds
                    db_match_bets_aux[bet_slug].url = bet.url
                    db_match_bets_aux[bet_slug].updated_at = datetime.utcnow()
                else:
                    db_match_bets_aux[bet_slug] = BetInDB(**bet.dict(), slug=bet_slug)
            db_match.bets = list(db_match_bets_aux.values())
            db_match.updated_at = datetime.utcnow()
            match_dict = db_match.dict()
            await self.client.update_one({"slug": slug}, {"$set": match_dict})
        except EntityDoesNotExist:
            # Create Match
            match_dict = match.dict()
            for idx, bet in enumerate(match.bets):
                match_dict["bets"][idx]["slug"] = self._bets_repository.get_bet_slug(match, bet)
            match_dict["slug"] = slug
            self.client.insert_one(MatchInDB(**match_dict).dict())
        return Match(**match_dict)

    @staticmethod
    def _get_match_slug(match: MatchBase) -> str:
        return slugify(
            ','.join(match.teams + list(map(str, (match.sport, match.tournament,
                                                  int(mktime(match.commence_time.timetuple())))))))


