from fastapi import APIRouter

from .endpoints import matches

router = APIRouter()
router.include_router(matches.router, tags=["matches"], prefix="/matches")
