from typing import Optional
import datetime

from fastapi import Depends, HTTPException, Path, Query
from starlette import status

from .database import get_repository

from ...db.errors import EntityDoesNotExist
from ...db.repositories.matches import MatchesRepository
from app.resources import strings

from ...models.matches import MatchFilterParams, Match, MatchInDB


def get_matches_filters(
    commence_day: datetime.date,
    sport: str,
    tournament: Optional[str] = None
) -> MatchFilterParams:
    return MatchFilterParams(
        commence_day=commence_day, sport=sport, tournament=tournament
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