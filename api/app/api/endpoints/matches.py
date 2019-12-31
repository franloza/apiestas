from fastapi import APIRouter

router = APIRouter()

@router.get(
    '/',
    response_model=ListOfMatchesInResponse,
    name="matches:list-matches"
)
async def list_matches(
    matches_filters: MatchesFilters = Depends(get_matches_filters),
    matches_repo : MatchesRepository = Depends(get_repository(MatchesRepository)),
) -> ListOfMatchesRepository:
    matches = await  matches_repo.filter_matches(
        commence_day=matches_filters.commence_day,
        sport=matches_filters.sport,
        tournament=matches_filters.tournament,
    )
    return ListOfMatchesInResponse(matches=matches, matches_count=len(matches))

#GET /matches?commence_day=209190902&sport=soccer&tournament=EPL
#PUT /matches
#PUT /matches/{match_key}/bet
#GET /matches/find?commence_time=1535205600&sport=soccer&team_1=Bournemouth&team_2=Everton&similarity=0.9

