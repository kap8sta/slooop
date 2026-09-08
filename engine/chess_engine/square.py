from __future__ import annotations

from dataclasses import dataclass

from chess_engine.types import Vector


@dataclass(frozen=True)
class Square:
    row: int
    col: int

    # file = notation[0], rank = notation[1]
    # board[row][col] = file + rank (board[6][4] = "e2")
    # row, col = rank, file (6, 4 = "2", "e")
    # I know
    @classmethod
    def from_notation(cls, notation: str) -> Square:
        col = ord(notation[0]) - ord("a")
        row = 8 - int(notation[1])

        return cls(row, col)

    def to_notation(self) -> str:
        file = chr(self.col + ord("a"))
        rank = str(8 - self.row)

        return file + rank

    @property
    def is_valid(self) -> bool:
        return 0 <= self.row < 8 and 0 <= self.col < 8

    def __add__(self, vector: Vector) -> Square:
        return Square(self.row + vector.row, self.col + vector.col)

    @classmethod
    def from_string(cls, notation: str) -> Square:
        return cls.from_notation(notation)
