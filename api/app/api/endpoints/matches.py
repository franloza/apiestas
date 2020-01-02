from fastapi import APIRouter, Depends, Body, Path, HTTPException
from starlette.status import HTTP_404_NOT_FOUND

from app.api.dependencies.database import get_repository
from app.api.dependencies.matches import get_matches_filters
from app.db.errors import EntityDoesNotExist
from app.db.repositories.matches import MatchesRepository
from app.resources.strings import MATCH_DOES_NOT_EXIST_ERROR
from app.models.matches import ManyMatchesInResponse, MatchFilterParams, MatchInResponse, MatchInUpsert, Match

router = APIRouter()

@router.get(
    '/',
    response_model=ManyMatchesInResponse,
    name="matches:list-matches"
)
async def list_matches(
    matches_filters: MatchFilterParams = Depends(get_matches_filters),
    matches_repo : MatchesRepository = Depends(get_repository(MatchesRepository)),
) -> ManyMatchesInResponse:
    matches = await matches_repo.filter_matches(
        commence_day=matches_filters.commence_day,
        sport=matches_filters.sport,
        tournament=matches_filters.tournament,
    )
    return ManyMatchesInResponse(matches=matches, matches_count=len(matches))

@router.get(
    '/{slug}',
    response_model=Match,
    name="matches:get-match"
)
async def get_match(
    slug: str = Path(..., min_length=1),
    matches_repo : MatchesRepository = Depends(get_repository(MatchesRepository)),
) -> Match:
    try:
        match = await matches_repo.get_match_by_slug(slug=slug)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=MATCH_DOES_NOT_EXIST_ERROR,
        )
    return Match(**match.dict())


@router.put(
    '/',
    response_model=MatchInResponse,
    name="matches:upsert-match"
)
async def upsert_matches(
    match: MatchInUpsert,
    matches_repo : MatchesRepository = Depends(get_repository(MatchesRepository)),
) -> MatchInResponse:
    match = await matches_repo.upsert_match(match=match)
    return MatchInResponse(match=match, bets_count=len(match.bets))
