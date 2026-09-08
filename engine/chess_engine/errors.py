class ChessEngineError(Exception):
    """Base exception for chess engine."""


class InvalidFenError(ChessEngineError):
    """FEN is invalid."""


class InvalidMoveError(ChessEngineError):
    """Move has invalid syntax."""


class IllegalMoveError(ChessEngineError):
    """Move is syntactically valid but illegal in the given position."""
