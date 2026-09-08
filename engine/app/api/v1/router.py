from fastapi import APIRouter

from app.api.v1.chess import router as chess_router

router = APIRouter()
router.include_router(chess_router, prefix="/chess", tags=["chess"])
