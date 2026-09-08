from __future__ import annotations

from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from chess_engine.types import GameStatus


class ApiGameStatus(str, Enum):
    CHECKMATE = "checkmate"
    STALEMATE = "stalemate"
    DRAW = "draw"
    ONGOING = "ongoing"

    @classmethod
    def from_domain(cls, status: GameStatus) -> ApiGameStatus:
        return cls[status.name]


UciMove = Annotated[
    str,
    Field(
        min_length=4,
        max_length=5,
        pattern=r"^[a-h][1-8][a-h][1-8][qrbn]?$",
        description="Move in UCI format",
        examples=["e2e4", "e7e8q"],
    ),
]

UciMoveList = list[UciMove]

FenString = Annotated[
    str,
    Field(
        pattern=r"^([pnbrqkPNBRQK1-8]+/){7}[pnbrqkPNBRQK1-8]+ [wb] (-|[KQkq]{1,4}) (-|[a-h][36]) \d+ [1-9]\d*$",
        description="Position on board in FEN format",
        examples=["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"],
    ),
]


class StartNewGameResponse(BaseModel):
    fen: FenString
    side_to_move: Literal["white", "black"]
    game_status: ApiGameStatus
    legal_moves: UciMoveList


class LegalMovesRequest(BaseModel):
    fen: FenString


class LegalMovesResponse(BaseModel):
    moves: UciMoveList


class MakeMoveRequest(BaseModel):
    fen: FenString
    move: UciMove


class MakeMoveResponse(BaseModel):
    fen: FenString | None = None
    side_to_move: Literal["white", "black"] | None = None
    game_status: ApiGameStatus | None = None
    legal_moves: UciMoveList | None = None
