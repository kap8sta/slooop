from __future__ import annotations

from chess_engine.square import Square
from chess_engine.types import Color, Piece, PieceType


class Board:
    @classmethod
    def _starting_grid(cls) -> list[list[Piece]]:
        return [
            [
                Piece.BLACK_ROOK,
                Piece.BLACK_KNIGHT,
                Piece.BLACK_BISHOP,
                Piece.BLACK_QUEEN,
                Piece.BLACK_KING,
                Piece.BLACK_BISHOP,
                Piece.BLACK_KNIGHT,
                Piece.BLACK_ROOK,
            ],
            [Piece.BLACK_PAWN] * 8,
            [Piece.EMPTY] * 8,
            [Piece.EMPTY] * 8,
            [Piece.EMPTY] * 8,
            [Piece.EMPTY] * 8,
            [Piece.WHITE_PAWN] * 8,
            [
                Piece.WHITE_ROOK,
                Piece.WHITE_KNIGHT,
                Piece.WHITE_BISHOP,
                Piece.WHITE_QUEEN,
                Piece.WHITE_KING,
                Piece.WHITE_BISHOP,
                Piece.WHITE_KNIGHT,
                Piece.WHITE_ROOK,
            ],
        ]

    @classmethod
    def starting(cls) -> Board:
        return cls(cls._starting_grid())

    @classmethod
    def empty(cls) -> Board:
        return cls([[Piece.EMPTY for _ in range(8)] for _ in range(8)])

    def __init__(self, board: list[list[Piece]] | None = None) -> None:
        self.board = board if board is not None else self._starting_grid()

    def __getitem__(self, square: Square) -> Piece:
        return self.board[square.row][square.col]

    def __setitem__(self, square: Square, piece: Piece) -> None:
        self.board[square.row][square.col] = piece

    def copy(self) -> Board:
        return Board([row.copy() for row in self.board])

    def set_piece(self, square: Square, piece: Piece) -> None:
        self[square] = piece

    def get_piece(self, square: Square) -> Piece:
        return self[square]

    def remove_piece(self, square: Square) -> None:
        self.set_piece(square, Piece.EMPTY)

    def move_piece(self, from_square: Square, to_square: Square) -> None:
        piece = self[from_square]
        self.set_piece(to_square, piece)
        self.remove_piece(from_square)

    def find_king(self, color: Color) -> Square:
        for row_idx, row in enumerate(self.board):
            for col_idx, piece in enumerate(row):
                if piece.piece_type == PieceType.KING and piece.piece_color == color:
                    return Square(row_idx, col_idx)
        raise ValueError("Король не найден!")

    def print_board(self) -> None:
        for row in self.board:
            print(" ".join(str(piece) for piece in row))

    def iter_pieces(self):
        for row_idx, row in enumerate(self.board):
            for col_idx, piece in enumerate(row):
                yield Square(row_idx, col_idx), piece
