from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Color(Enum):
    WHITE = "white"
    BLACK = "black"


class PieceType(Enum):
    EMPTY = "."

    PAWN = "p"
    KNIGHT = "n"
    BISHOP = "b"
    ROOK = "r"
    QUEEN = "q"
    KING = "k"


class Piece(Enum):
    EMPTY = "."

    WHITE_PAWN = "P"
    WHITE_KNIGHT = "N"
    WHITE_BISHOP = "B"
    WHITE_ROOK = "R"
    WHITE_QUEEN = "Q"
    WHITE_KING = "K"

    BLACK_PAWN = "p"
    BLACK_KNIGHT = "n"
    BLACK_BISHOP = "b"
    BLACK_ROOK = "r"
    BLACK_QUEEN = "q"
    BLACK_KING = "k"

    def __str__(self):
        return self.value

    @classmethod
    def from_type_and_color(cls, piece_type: PieceType, color: Color) -> Piece:
        char = piece_type.value.upper() if color == Color.WHITE else piece_type.value.lower()
        return cls(char)

    # либо сделать EMPTY == None, либо оставить проверки на PieceType.EMPTY
    @property
    def piece_type(self) -> PieceType:
        return PieceType(self.value.lower())

    @property
    def piece_color(self) -> Color | None:
        if self == Piece.EMPTY:
            return None

        return Color.WHITE if self.value.isupper() else Color.BLACK

    @property
    def is_empty(self) -> bool:
        return self is Piece.EMPTY


@dataclass(frozen=True)
class Vector:
    row: int
    col: int


UP = Vector(-1, 0)
DOWN = Vector(1, 0)
LEFT = Vector(0, -1)
RIGHT = Vector(0, 1)
UP_LEFT = Vector(-1, -1)
UP_RIGHT = Vector(-1, 1)
DOWN_LEFT = Vector(1, -1)
DOWN_RIGHT = Vector(1, 1)

KNIGHT_OFFSETS = (
    Vector(1, 2),
    Vector(2, 1),
    Vector(-1, 2),
    Vector(-2, 1),
    Vector(1, -2),
    Vector(2, -1),
    Vector(-1, -2),
    Vector(-2, -1),
)

ORTHOGONAL_DIRECTIONS = (
    UP,
    DOWN,
    LEFT,
    RIGHT,
)

DIAGONAL_DIRECTIONS = (
    UP_LEFT,
    UP_RIGHT,
    DOWN_LEFT,
    DOWN_RIGHT,
)

ALL_DIRECTIONS = (
    *ORTHOGONAL_DIRECTIONS,
    *DIAGONAL_DIRECTIONS,
)


@dataclass
class CastlingRights:
    white_kingside: bool = True
    white_queenside: bool = True
    black_kingside: bool = True
    black_queenside: bool = True

    @property
    def any_white(self) -> bool:
        return self.white_kingside or self.white_queenside

    @property
    def any_black(self) -> bool:
        return self.black_kingside or self.black_queenside

    def kingside(self, color: Color) -> bool:
        return self.white_kingside if color == Color.WHITE else self.black_kingside

    def queenside(self, color: Color) -> bool:
        return self.white_queenside if color == Color.WHITE else self.black_queenside


WHITE_HOME_RANK = 7
WHITE_PAWN_RANK = 6
BLACK_HOME_RANK = 0
BLACK_PAWN_RANK = 1


PROMOTION_PIECES = [
    PieceType.QUEEN,
    PieceType.ROOK,
    PieceType.BISHOP,
    PieceType.KNIGHT,
]


class GameStatus(Enum):
    CHECKMATE = "checkmate"
    STALEMATE = "stalemate"
    DRAW = "draw"
    ONGOING = "ongoing"
