from __future__ import annotations

from dataclasses import dataclass

from chess_engine.square import Square
from chess_engine.types import PieceType


@dataclass(frozen=True)
class Move:
    from_square: Square
    to_square: Square
    promotion: PieceType | None = None
    is_castling: bool = False
    is_en_passant: bool = False

    def to_uci(self) -> str:
        uci = self.from_square.to_notation() + self.to_square.to_notation()
        if self.promotion is not None:
            uci += self.promotion.value
        return uci

    @classmethod
    def from_uci(cls, uci: str) -> Move:
        from_square = Square.from_notation(uci[0:2])
        to_square = Square.from_notation(uci[2:4])
        promotion = PieceType(uci[4]) if len(uci) > 4 else None
        return cls(from_square=from_square, to_square=to_square, promotion=promotion)
