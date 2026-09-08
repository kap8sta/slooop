import pytest

from chess_engine.chess_engine import ChessEngine
from chess_engine.position import Position

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
EN_PASSANT_FEN = "rnbqkbnr/pppp1ppp/8/2p1P3/3p4/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 3"
CHECK_FEN = "rnbqkbnr/pppp1Qpp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 2"
CHECKMATE_FEN = "7k/6Q1/6K1/8/8/8/8/8 b - - 0 1"
PRE_CHECKMATE_FEN = "7k/5Q2/6K1/8/8/8/8/8 w - - 0 1"
STALEMATE_FEN = "7k/5Q2/5RK1/8/8/8/8/8 b - - 0 1"
CASTLING_FEN = "rnbqk2r/pppp1ppp/4bn2/8/8/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1"
CASTLING_THROUGH_CHECK_FEN = "4k2r/8/8/8/8/8/4q4/R3K2R w KQ - 0 1"


@pytest.fixture
def starting_position():
    return Position.starting()


@pytest.fixture
def starting_fen():
    return STARTING_FEN


@pytest.fixture
def engine():
    return ChessEngine()


@pytest.fixture
def engine_from_fen(starting_fen):
    return ChessEngine(Position.from_fen(starting_fen))
