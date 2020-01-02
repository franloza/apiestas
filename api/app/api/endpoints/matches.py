from typing import List

from fastapi import APIRouter, Depends, Body, Path, HTTPException, Query
from fuzzywuzzy import fuzz
from slugify import slugify
from starlette import status
from starlette.status import HTTP_404_NOT_FOUND

from app.api.dependencies.database import get_repository
from app.api.dependencies.matches import get_matches_filters, get_match_by_slug_from_path
from app.db.errors import EntityDoesNotExist
from app.db.repositories.matches import MatchesRepository
from app.resources import strings
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
    matches = await matches_repo.filter_matches(commence_day=matches_filters.commence_day,
                                                commence_time=matches_filters.commence_time,
                                                sport=matches_filters.sport,
                                                tournament=matches_filters.tournament)
    return ManyMatchesInResponse(matches=matches, matches_count=len(matches))


@router.get(
    '/find',
    response_model=Match,
    name="matches:find-matches"
)
async def find_match(
    teams: List[str] = Query(...),
    matches_filters: MatchFilterParams = Depends(get_matches_filters),
    similarity: int = Query(70, min=0, max=100),
    matches_repo: MatchesRepository = Depends(get_repository(MatchesRepository)),
) -> Match:
    matches = await matches_repo.filter_matches(commence_day=matches_filters.commence_day,
                                                commence_time=matches_filters.commence_time,
                                                sport=matches_filters.sport,
                                                tournament=matches_filters.tournament)
    if not matches:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=strings.MATCH_WAS_NOT_FOUND_ERROR,
        )

    found_matches = []
    teams_slug = slugify(' '.join(teams))
    for match in matches:
        match_teams_slug = slugify(' '.join(match.teams))
        score = fuzz.partial_ratio(teams_slug, match_teams_slug)
        if score > similarity:
            found_matches.append(match)
    if not found_matches:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=strings.MATCH_WAS_NOT_FOUND_ERROR,
        )
    elif len(found_matches) > 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=strings.MORE_THAN_ONE_MATCH_FOUND_ERROR,
        )
    return found_matches[0]


@router.get(
    '/{slug}',
    response_model=Match,
    name="matches:get-match"
)
async def get_match(match = Depends(get_match_by_slug_from_path)) -> Match:
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
