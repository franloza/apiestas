from collections import OrderedDict
from datetime import datetime
from time import mktime
from typing import List

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from slugify import slugify

from app.db.errors import EntityDoesNotExist
from app.db.repositories.base import BaseRepository
from app.db.repositories.bets import BetsRepository
from app.models.matches import Match, MatchInUpsert, MatchBase


class MatchesRepository(BaseRepository):
    def __init__(self, client: AsyncIOMotorDatabase) -> None:
        super().__init__(client)
        self._client = self._client["matches"]
        self._bets_repository = BetsRepository(client)

    async def get_match_by_slug(self, slug: str) -> Match:
        doc = await self.client.find_one({"slug": slug})
        if doc:
            return Match(
                **doc,
                created_at=ObjectId(doc["_id"]).generation_time
            )
        else:
            raise EntityDoesNotExist("match with slug {0} does not exist".format(slug))

    async def filter_matches(self, commence_day: datetime.date, sport : str, tournament :  str = None) -> List[Match]:
        query = {"sport": sport}
        if tournament:
            query["tournament"] = tournament
        matches_docs = await self.client.find(query)
        return [Match(**match) for match in matches_docs]

    async def upsert_match(self, match: MatchInUpsert) -> Match:
        slug = await self.get_match_slug(match)
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
                    db_match_bets_aux[bet_slug].updated_at = datetime.now()
                else:
                    db_match_bets_aux[bet_slug] = bet
            db_match.bets = list(db_match_bets_aux.values())
            self.client.update_one({"slug": slug}, db_match)
        except EntityDoesNotExist:
            # Create Match
            db_match = match.copy(include={'slug': slug})
            self.client.insert_one(db_match)
        return db_match

    async def get_match_slug(self, match: MatchBase) -> str:
        return slugify(' '.join(match.teams + [match.sport, match.tournament, mktime(match.commence_time.timetuple())]))


