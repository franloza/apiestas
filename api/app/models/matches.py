import datetime
from typing import List, Optional

from pydantic import Field

from .bets import Bet, BetInUpsert, BetInDB
from .common import DateTimeModelMixin
from .enums import Sport
from .rwmodel import RWModel


class MatchBase(RWModel):
    sport: Sport = Field(..., example="football")
    tournament: str  = Field(..., example="Premier League")
    teams: List[str] = Field(..., description="In two-team sports, the first element correspond to the home team",
                             example=["Brighton", "Bournemouth"], min_items=2)
    commence_time: datetime.datetime
    bets: List[Bet]


class Match(DateTimeModelMixin, MatchBase):
    slug: str = Field(..., example="brighton-bournemouth-football-premier-league-1577536200")


class MatchInDB(Match):
    bets: List[BetInDB]
    feed: str


class MatchInResponse(RWModel):
    match: Match
    bets_count: int


class MatchFilterParams(RWModel):
    commence_day: Optional[datetime.date] = None
    commence_time: Optional[datetime.datetime] = None
    sport: Sport
    tournament: Optional[str]


class ManyMatchesInResponse(RWModel):
    matches: List[Match]
    matches_count : int


class MatchInUpsert(MatchBase):
    feed: str
    bets: Optional[List[BetInUpsert]] = []









