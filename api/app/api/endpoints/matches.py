from fastapi import APIRouter, Depends

from app.api.dependencies.database import get_repository
from app.api.dependencies.matches import get_matches_filters
from app.db.repositories.matches import MatchesRepository
from app.models.matches import ManyMatchesInResponse, MatchFilterParams

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

#GET /matches?commence_day=209190902&sport=soccer&tournament=EPL
#PUT /matches
#PUT /matches/{match_key}/bet
#GET /matches/find?commence_time=1535205600&sport=soccer&team_1=Bournemouth&team_2=Everton&similarity=0.9

