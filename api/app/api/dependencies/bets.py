from typing import Optional
import datetime

from fastapi import Depends, HTTPException, Path
from starlette import status

from .database import get_repository

from ...db.errors import EntityDoesNotExist
from ...db.repositories.bets import BetsRepository
from app.resources import strings

from ...models.bets import BetInDB


async def get_bet_by_slug_from_path(
    slug: str = Path(..., min_length=1),
    bets_repo: BetsRepository = Depends(get_repository(BetsRepository)),
) -> BetInDB:
    try:
        return await bets_repo.get_bet_by_slug(slug=slug)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=strings.BET_DOES_NOT_EXIST_ERROR,
        )