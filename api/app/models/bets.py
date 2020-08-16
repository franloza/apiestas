from typing import List, Optional

from pydantic import Field

from .common import DateTimeModelMixin
from .rwmodel import RWModel


class BetBase(RWModel):
    bookmaker: str = Field(..., example="bet365")
    bookmaker_nice: str = Field(..., example="Bet365")
    bet_type: str = Field(..., example='1X2')
    bet_scope: str = Field(..., example='Full time')
    is_back: bool = Field(..., description="If the bet is back (True) or lay (False)")
    url: Optional[str] = Field(None, example= "http://www.bet365.com/betslip/instantbet/...")
    odds: List[float] = Field(...,
                              description="Odds are in the same order as teams. For 3 outcome sports, "
                                          "the 3rd item in the list is the draw odd.", min_items=2,
                              example=[1.8, 4.33, 3.75]
                              )


class Bet(DateTimeModelMixin, BetBase):
    slug: str = Field(..., example="brighton-bournemouth-football-premier-league-bet365")


class BetInDB(Bet):
    feed: str


class BetInResponse(RWModel):
    bet: Bet


class BetFilterParams(RWModel):
    bookmaker: str


class ManyBetsInResponse(RWModel):
    bets: List[Bet]


class BetInUpsert(BetBase):
    feed: str








