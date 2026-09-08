from typing import Annotated

from fastapi import APIRouter, Depends

from app.schemas.chess import (
    LegalMovesRequest,
    LegalMovesResponse,
    MakeMoveRequest,
    MakeMoveResponse,
    StartNewGameResponse,
)
from app.services.chess_service import ChessService

router = APIRouter()


def get_chess_service() -> ChessService:
    return ChessService()


ChessServiceDep = Annotated[ChessService, Depends(get_chess_service)]


@router.get("/start-new-game", response_model=StartNewGameResponse)
def start_new_game(service: ChessServiceDep) -> StartNewGameResponse:
    return service.start_new_game()


@router.post("/legal-moves", response_model=LegalMovesResponse)
def legal_moves(
    payload: LegalMovesRequest,
    service: ChessServiceDep,
) -> LegalMovesResponse:
    moves = service.legal_moves(payload.fen)
    return LegalMovesResponse(moves=moves)


@router.post("/make-move", response_model=MakeMoveResponse)
def make_move(
    payload: MakeMoveRequest,
    service: ChessServiceDep,
) -> MakeMoveResponse:
    return service.make_move(payload.fen, payload.move)
