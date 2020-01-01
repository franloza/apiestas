import datetime
from typing import List

from app.models.bets import Bet
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


class MatchInDB(MatchBase, DateTimeModelMixin):
    feed: str


class MatchInResponse(RWModel):
    match: Match
    bets: List[Bet]
    bets_count: int


class MatchFilterParams(RWModel):
    commence_day: datetime.date
    sport: str
    tournament: str


class ManyMatchesInResponse(RWModel):
    matches: List[Match]
    matches_count : int


class MatchInUpsert(MatchBase):
    feed: str









