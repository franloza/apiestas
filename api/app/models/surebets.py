from datetime import datetime, date
from typing import List, Optional

from pydantic import Field

from .common import DateTimeModelMixin
from .enums import Sport
from .rwmodel import RWModel


class Outcome(RWModel):
    bookmaker: str = Field(..., example="bet365")
    bookmaker_nice: str = Field(..., example="Bet365")
    url: Optional[str] = Field(None, example="http://www.bet365.com/betslip/instantbet/...")
    odd: float = Field(..., example=9.50)


class SureBetBase(RWModel):
    bet_type: str = Field(..., example='1X2')
    bet_scope: str = Field(..., example='Full time')
    is_back: bool = Field(..., description="If the bet is back (True) or lay (False)")
    outcomes: List[Outcome] = Field(...,
                                    description="Outcomes provided for every bookmaker in order. For 3 outcome sports, "
                                                "the 3rd item in the list is the draw odd.", min_items=2,
                                    max_items=3
                                    )
    profit: float = Field(..., description="Profit of the surebet", example=0.06)


class SureBet(DateTimeModelMixin, SureBetBase):
    slug: str = Field(..., example="brighton-bournemouth-football-premier-league-1597350600-1x2-full-time-false-bet365-pinnacle")


class SureBetInDB(SureBet):
    pass


class SureBetInResponse(RWModel):
    sport: Sport = Field(..., example="football")
    tournament: str = Field(..., example="premier-league")
    tournament_nice: str = Field(..., example="Premier League")
    teams: List[str] = Field(..., description="In two-team sports, the first element correspond to the home team",
                             example=["Brighton", "Bournemouth"], min_items=2)
    commence_time: datetime
    url: str
    surebet: SureBet


class SureBetFilterParams(RWModel):
    commence_day: Optional[date]
    min_profit: Optional[float]
    sport: Optional[Sport]


class ManySureBetsInResponse(RWModel):
    surebets: List[SureBetInResponse]
    surebets_count: int


class SureBetInUpsert(SureBetBase):
    pass