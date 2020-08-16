from fastapi import APIRouter

from .endpoints import matches, bets, surebets

router = APIRouter()
router.include_router(matches.router, tags=["matches"], prefix="/matches")
router.include_router(bets.router, tags=["bets"], prefix="/matches/bets")
router.include_router(surebets.router, tags=["surebets"], prefix="/matches/surebets")
