from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from fuzzywuzzy import fuzz
from slugify import slugify
from starlette import status

from ...api.dependencies.database import get_repository
from ...api.dependencies.matches import get_matches_filters, get_match_by_slug_from_path
from ...db.repositories.bets import BetsRepository
from ...db.repositories.matches import MatchesRepository
from ...models.bets import Bet, BetInUpsert
from ...resources import strings
from ...models.matches import (
    ManyMatchesInResponse, MatchFilterParams, MatchInResponse, MatchInUpsert, Match, MatchInDB)

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
    """
    Get a list of matches that fulfil the specified filtering criteria

    - **commence_day**: Date of commence of the match. If **commence_time** is not specified, it sets
    today as default.
    - **commence_time**: Datetime of commence of the match (UTC). It process either a unix timestamp int
    (e.g. 1496498400) or a string representing the date & time.
    - **sport**: Name of the sport
    - **tournament**: Name of the tournament
    """
    matches = await matches_repo.filter_matches(commence_day=matches_filters.commence_day,
                                                commence_time=matches_filters.commence_time,
                                                sport=matches_filters.sport,
                                                tournament=matches_filters.tournament)
    return ManyMatchesInResponse(matches=matches, matches_count=len(matches))


@router.get(
    '/find',
    response_model=Match,
    name="matches:find-matches",
    responses={404: {"description": "Any match has a similarity higher than the given threshold"}}
)
async def find_match(
    teams: List[str] = Query(..., min_items=2),
    matches_filters: MatchFilterParams = Depends(get_matches_filters),
    similarity: int = Query(70, min=0, max=100),
    matches_repo: MatchesRepository = Depends(get_repository(MatchesRepository)),
) -> Match:
    """
    Do a fuzzy search using team names to find a match. We recommend to specify as filters as possible (e.g. specific
    commence time) to speed up retrieval process and avoid retrieving more than one match. It uses Partial Ratio
    between two slugs obtained from team names.

    - **teams**: Name of the teams that participate in the match.
    - **commence_day**: Date of commence of the match. If **commence_time** is not specified, it sets
    today as default.
    - **commence_time**: Datetime of commence of the match (UTC). It process either a unix timestamp int
    (e.g. 1496498400) or a string representing the date & time.
    - **sport**: Name of the sport
    - **tournament**: Name of the tournament
    - **similarity**: Similarity threshold. Value ranges from 0 to 100 and it means the minimum amount of similarity
    with the match teams. By default, the threshold is 70
    """
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
async def upsert_match(
    match: MatchInUpsert,
    matches_repo : MatchesRepository = Depends(get_repository(MatchesRepository)),
) -> MatchInResponse:
    match = await matches_repo.upsert_match(match=match)
    return MatchInResponse(match=match, bets_count=len(match.bets))


@router.put(
    '/{slug}/bets',
    response_model=Bet,
    name="bets:upsert-bet"
)
async def upsert_bet(
        bet: BetInUpsert,
        match: MatchInDB = Depends(get_match_by_slug_from_path),
        bets_repo:  BetsRepository = Depends(get_repository(BetsRepository)),
) -> Bet:
    bet = await bets_repo.upsert_bet(match=match, bet=bet)
    return bet
