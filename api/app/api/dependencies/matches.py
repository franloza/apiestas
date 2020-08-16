from typing import Optional
import datetime

from fastapi import Depends, HTTPException, Path
from starlette import status

from .database import get_repository

from ...db.errors import EntityDoesNotExist
from ...db.repositories.matches import MatchesRepository
from ...models.surebets import SureBetFilterParams
from ...resources import strings
from ...models.matches import MatchFilterParams , MatchInDB
from ...models.enums import Sport


def get_matches_filters(
    sport: Sport,
    commence_day: Optional[datetime.date] = datetime.datetime.utcnow().date(),
    tournament: Optional[str] = None,
    commence_time: Optional[datetime.datetime] = None
) -> MatchFilterParams:
    return MatchFilterParams(
        commence_day=commence_day, sport=sport, tournament=tournament, commence_time=commence_time
    )


def get_surebets_filters(
    sport: Optional[Sport] = None,
    commence_day: Optional[datetime.date] = None,
    min_profit: Optional[float] = None
) -> SureBetFilterParams:
    return SureBetFilterParams(
        commence_day=commence_day, sport=sport, min_profit=min_profit
    )


async def get_match_by_slug_from_path(
    slug: str = Path(..., min_length=1),
    matches_repo: MatchesRepository = Depends(get_repository(MatchesRepository)),
) -> MatchInDB:
    try:
        return await matches_repo.get_match_by_slug(slug=slug)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=strings.MATCH_DOES_NOT_EXIST_ERROR,
        )


async def check_by_slug_from_path(
    slug: str = Path(..., min_length=1),
    matches_repo: MatchesRepository = Depends(get_repository(MatchesRepository)),
) -> str:
    try:
        await matches_repo.get_match_id_by_slug(slug=slug)
        return slug
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=strings.MATCH_DOES_NOT_EXIST_ERROR,
        )