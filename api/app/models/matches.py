import datetime
from typing import List, Optional

from app.models.bets import Bet, BetInUpsert, BetInDB
from app.models.common import DateTimeModelMixin
from app.models.rwmodel import RWModel


class MatchBase(RWModel):
    sport: str
    tournament: str
    teams: List[str]
    commence_time: datetime.datetime
    bets: List[Bet]


class Match(DateTimeModelMixin, MatchBase):
    slug: str


class MatchInDB(Match):
    bets: List[BetInDB]
    feed: str


class MatchInResponse(RWModel):
    match: Match
    bets_count: int


class MatchFilterParams(RWModel):
    commence_day: datetime.date
    sport: str
    tournament: Optional[str]


class ManyMatchesInResponse(RWModel):
    matches: List[Match]
    matches_count : int


class MatchInUpsert(MatchBase):
    feed: str
    bets: List[BetInUpsert]









