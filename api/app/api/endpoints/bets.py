from fastapi import APIRouter, Depends

from ...api.dependencies.bets import get_bet_by_slug_from_path
from ...models.bets import Bet

router = APIRouter()


@router.get(
    '/{slug}',
    response_model=Bet,
    name="bets:get-bet"
)
async def get_bet(bet=Depends(get_bet_by_slug_from_path)) -> Bet:
    return Bet(**bet.dict())
