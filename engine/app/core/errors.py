from fastapi import Request
from fastapi.responses import JSONResponse

from chess_engine.errors import IllegalMoveError


async def illegal_move_handler(
    request: Request,
    exc: IllegalMoveError,
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"error": "ILLEGAL_MOVE"},
    )
