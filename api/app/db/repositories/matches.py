from collections import OrderedDict
from datetime import datetime, timedelta, date
import calendar
from typing import List

from motor.motor_asyncio import AsyncIOMotorDatabase
from slugify import slugify

from ...db.errors import EntityDoesNotExist
from ...db.repositories.base import BaseRepository
from ...db.repositories.bets import BetsRepository
from ...core.config import COLLECTION_NAME
from ...models.bets import BetInDB
from ...models.enums import Sport
from ...models.matches import Match, MatchInUpsert, MatchBase, MatchInDB
from ...models.surebets import SureBetInUpsert, SureBetBase, SureBet


class MatchesRepository(BaseRepository):
    def __init__(self, client: AsyncIOMotorDatabase) -> None:
        super().__init__(client)
        self._client = self._client[COLLECTION_NAME]
        self._bets_repository = BetsRepository(client)

    async def get_match_by_slug(self, slug: str) -> MatchInDB:
        doc = await self.client.find_one({"slug": slug})
        if doc:
            return MatchInDB(**doc)
        else:
            raise EntityDoesNotExist("match with slug {0} does not exist".format(slug))

    async def get_match_id_by_slug(self, slug: str) -> str:
        doc = await self.client.find_one({"slug": slug}, {"_id": 1})
        if doc:
            return doc["_id"]
        else:
            raise EntityDoesNotExist("match with slug {0} does not exist".format(slug))

    async def filter_matches(self, commence_day: datetime.date, sport: Sport = None, tournament:  str = None,
                             commence_time: datetime.date = None) -> List[Match]:
        query = {}
        if sport:
            query["sport"] = sport.value
        if commence_time:
            query["commence_time"] = commence_time
        else:
            commence_time = datetime.combine(commence_day, datetime.min.time())
            query["commence_time"] = {'$gte': commence_time, '$lt': commence_time + timedelta(days=1)}
        if tournament:
            query["tournament"] = tournament
        matches_docs = self.client.find(query, {"surebets": 0})
        return [Match(**match) async for match in matches_docs]

    async def filter_surebets(self, commence_day: datetime.date, sport: Sport = None, min_profit: float = None
                              ) -> List[MatchInDB]:
        query = {
            "surebets": {"$exists": True, "$ne": None, "$not": {"$size": 0}}
        }
        if sport:
            query["sport"] = sport.value
        if commence_day:
            commence_time = datetime.combine(commence_day, datetime.min.time())
            query["commence_time"] = {'$gte': commence_time, '$lt': commence_time + timedelta(days=1)}
        else:
            query["commence_time"] = {'$gte': datetime.utcnow()}
        projection = {'bets': 0}
        if min_profit:
            matches_docs = self.client.aggregate([
                {
                    '$match': query
                },
                # Filter surebets without minimum profit
                {
                    '$addFields': {
                        "surebets": {
                            "$filter": {
                                "input": "$surebets",
                                "as": "surebet",
                                "cond": {'$gte':  ["$$surebet.profit", min_profit]}
                            }
                        }
                    }
                },
                {'$project': projection},
                {'$match': query},
            ])
        else:
            matches_docs = self.client.find(query, projection)
        return [MatchInDB(**match, bets=[]) async for match in matches_docs]

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
                    created_at = db_match_bets_aux[bet_slug].created_at
                    db_match_bets_aux[bet_slug] = BetInDB(**bet.dict(), slug=bet_slug)
                    db_match_bets_aux[bet_slug].created_at = created_at
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

    async def create_surebets(self, match: Match, surebets: List[SureBetInUpsert]) -> None:
        db_surebets = []
        for surebet in surebets:
            db_surebets.append(SureBet(slug=self._get_surebet_slug(match, surebet), **surebet.dict()).dict())
        await self.client.update_one(
            {"slug": match.slug}, {"$set": {"surebets": db_surebets}})

    @staticmethod
    def _get_match_slug(match: MatchBase) -> str:
        return slugify(
            ','.join(match.teams + list(map(str, (match.sport.value, match.tournament,
                                                  calendar.timegm(match.commence_time.utctimetuple()))))))


    @staticmethod
    def _get_surebet_slug(match: MatchBase, surebet: SureBetBase) -> str:
        slug_elems = match.teams + [match.sport.value, match.tournament, calendar.timegm(match.commence_time.utctimetuple()),
                                    surebet.bet_type, surebet.bet_scope, surebet.is_back, surebet.outcomes[0].bookmaker,
                                    surebet.outcomes[1].bookmaker]
        if len(surebet.outcomes) > 2:
            slug_elems.append(surebet.outcomes[2].bookmaker)
        return slugify(','.join(map(str, slug_elems)))
