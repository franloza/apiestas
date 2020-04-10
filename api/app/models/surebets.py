from datetime import datetime
from typing import List, Optional

from pydantic import Field

from .common import DateTimeModelMixin
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
    profit: float = Field(..., description="Profit of the surebet")


class SureBet(DateTimeModelMixin, SureBetBase):
    slug: str = Field(..., example="brighton-bournemouth-football-premier-league-1x2-full-time-false-bet365-pinnacle")


class SureBetInResponse(RWModel):
    surebet: SureBet


class SureBetFilterParams(RWModel):
    profit: float


class ManyBetsInResponse(RWModel):
    surebets: List[SureBet]


class SureBetInUpsert(SureBetBase):
    pass