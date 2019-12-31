from typing import List, Optional

from app.models.common import DateTimeModelMixin
from app.models.rwmodel import RWModel


class BetBase(RWModel):
    bookmaker: str
    url: Optional[str] = None
    odds: List[float]


class Bet(DateTimeModelMixin, BetBase):
    slug: str


class BetInDB(BetBase, DateTimeModelMixin):
    feed: str


class BetInResponse(RWModel):
    bet: Bet


class BetFilterParams(RWModel):
    bookmaker: str


class ManyBetsInResponse(RWModel):
    bets: List[Bet]


class BetInUpsert(BetBase):
    feed: str








