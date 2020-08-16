from fastapi import APIRouter, Depends

from ..dependencies.database import get_repository
from ..dependencies.matches import get_surebets_filters
from ...db.repositories.matches import MatchesRepository
from ...models.surebets import SureBetFilterParams, SureBetInResponse, ManySureBetsInResponse

router = APIRouter()


@router.get(
    '/',
    response_model=ManySureBetsInResponse,
    name="surebets:list-surebets"
)
async def list_surebets(
        surebets_filters: SureBetFilterParams = Depends(get_surebets_filters),
        matches_repo: MatchesRepository = Depends(get_repository(MatchesRepository))
        ) -> ManySureBetsInResponse:
    """
    Get a list of sure bets that fulfil the specified filtering criteria
    """
    matches = await matches_repo.filter_surebets(commence_day=surebets_filters.commence_day,
                                                 sport=surebets_filters.sport,
                                                 min_profit=surebets_filters.min_profit)
    surebets = [
        SureBetInResponse(
            sport=match.sport,
            tournament=match.tournament,
            tournament_nice=match.tournament_nice,
            teams=match.teams,
            commence_time=match.commence_time,
            url=match.url,
            surebet=surebet
        ) for match in matches for surebet in match.surebets]
    return ManySureBetsInResponse(surebets=surebets, surebets_count=len(surebets))
