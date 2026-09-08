from fastapi import FastAPI

from app.api.v1.router import router as v1_router
from app.core.errors import illegal_move_handler
from chess_engine.errors import IllegalMoveError

app = FastAPI(
    title="Chess Engine API",
    version="0.7.42",
)

app.include_router(v1_router, prefix="/api/v1")

app.add_exception_handler(
    IllegalMoveError,
    illegal_move_handler,
)
