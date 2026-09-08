from __future__ import annotations

import copy
from dataclasses import dataclass, replace

from chess_engine.board import Board
from chess_engine.move import Move
from chess_engine.square import Square
from chess_engine.types import CastlingRights, Color, Piece, PieceType


@dataclass(frozen=True)
class Position:
    board: Board
    side_to_move: Color
    castling_rights: CastlingRights
    en_passant_square: Square | None
    halfmove_clock: int
    fullmove_number: int

    @classmethod
    def starting(cls) -> Position:
        return cls(
            board=Board.starting(),
            side_to_move=Color.WHITE,
            castling_rights=CastlingRights(),
            en_passant_square=None,
            halfmove_clock=0,
            fullmove_number=1,
        )

    def copy(self) -> Position:
        return replace(
            self,
            board=self.board.copy(),
            castling_rights=copy.copy(self.castling_rights),
        )

    def apply_move(self, move: Move) -> Position:
        new_board = self.board.copy()
        moving_piece = new_board[move.from_square]
        captured_piece = new_board[move.to_square]
        new_board.move_piece(move.from_square, move.to_square)
        en_passant_square: Square | None = None

        if move.is_castling:
            row = move.from_square.row
            if move.to_square.col == 6:
                rook_from, rook_to = Square(row, 7), Square(row, 5)
                new_board.move_piece(rook_from, rook_to)
            elif move.to_square.col == 2:
                rook_from, rook_to = Square(row, 0), Square(row, 3)
                new_board.move_piece(rook_from, rook_to)

        elif move.is_en_passant:
            captured_pawn_square = Square(move.from_square.row, move.to_square.col)
            new_board.remove_piece(captured_pawn_square)
            captured_piece = Piece.EMPTY

        elif move.promotion is not None:
            new_piece = Piece.from_type_and_color(move.promotion, self.side_to_move)
            new_board.set_piece(move.to_square, new_piece)

        if moving_piece.piece_type == PieceType.PAWN and abs(move.to_square.row - move.from_square.row) == 2:
            middle_row = (move.from_square.row + move.to_square.row) // 2
            en_passant_square = Square(middle_row, move.from_square.col)

        castling_rights = self._update_castling_rights(self.castling_rights, move, moving_piece)
        side_to_move = Color.BLACK if self.side_to_move == Color.WHITE else Color.WHITE

        is_capture = not captured_piece.is_empty or move.is_en_passant
        is_pawn_move = moving_piece.piece_type == PieceType.PAWN
        halfmove_clock = 0 if is_capture or is_pawn_move else self.halfmove_clock + 1
        fullmove_number = self.fullmove_number + 1 if self.side_to_move == Color.BLACK else self.fullmove_number

        return Position(
            board=new_board,
            side_to_move=side_to_move,
            castling_rights=castling_rights,
            en_passant_square=en_passant_square,
            halfmove_clock=halfmove_clock,
            fullmove_number=fullmove_number,
        )

    @staticmethod
    def _update_castling_rights(
        castling_rights: CastlingRights,
        move: Move,
        moving_piece: Piece,
    ) -> CastlingRights:
        rights = copy.copy(castling_rights)

        if moving_piece == Piece.WHITE_KING:
            rights.white_kingside = False
            rights.white_queenside = False
        elif moving_piece == Piece.BLACK_KING:
            rights.black_kingside = False
            rights.black_queenside = False

        if move.from_square == Square.from_notation("a1"):
            rights.white_queenside = False
        elif move.from_square == Square.from_notation("h1"):
            rights.white_kingside = False
        elif move.from_square == Square.from_notation("a8"):
            rights.black_queenside = False
        elif move.from_square == Square.from_notation("h8"):
            rights.black_kingside = False

        if move.to_square == Square.from_notation("a1"):
            rights.white_queenside = False
        elif move.to_square == Square.from_notation("h1"):
            rights.white_kingside = False
        elif move.to_square == Square.from_notation("a8"):
            rights.black_queenside = False
        elif move.to_square == Square.from_notation("h8"):
            rights.black_kingside = False

        return rights

    @staticmethod
    def _parse_castling_rights(castling_part: str) -> CastlingRights:
        if castling_part == "-":
            return CastlingRights(False, False, False, False)

        return CastlingRights(
            white_kingside="K" in castling_part,
            white_queenside="Q" in castling_part,
            black_kingside="k" in castling_part,
            black_queenside="q" in castling_part,
        )

    @staticmethod
    def _parse_board(board_part: str) -> Board:
        rows = board_part.split("/")
        board = Board.empty()

        for row_idx, row in enumerate(rows):
            board_col_idx = 0
            for char in row:
                if char.isdigit():
                    board_col_idx += int(char)
                elif char.isalpha():
                    piece = Piece(char)
                    board.board[row_idx][board_col_idx] = piece
                    board_col_idx += 1

        return board

    @classmethod
    def from_fen(cls, fen_string: str) -> Position:
        parts = fen_string.strip().split(" ")
        if len(parts) != 6:
            raise ValueError(f"Неверный формат FEN. Ожидалось 6 блоков, получено {len(parts)}")

        board_part, turn_part, castling_part, en_passant_part, halfmove_part, fullmove_part = parts
        turn = Color.WHITE if turn_part == "w" else Color.BLACK
        en_passant_square = None if en_passant_part == "-" else Square.from_notation(en_passant_part)
        castling_rights = cls._parse_castling_rights(castling_part)
        board = cls._parse_board(board_part)

        return cls(
            board=board,
            side_to_move=turn,
            castling_rights=castling_rights,
            en_passant_square=en_passant_square,
            halfmove_clock=int(halfmove_part),
            fullmove_number=int(fullmove_part),
        )

    def _board_to_fen(self) -> str:
        fen_rows = []
        for row in range(8):
            empty_count = 0
            row_str = ""
            for col in range(8):
                piece = self.board.board[row][col]
                if piece.piece_type == PieceType.EMPTY:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        row_str += str(empty_count)
                        empty_count = 0
                    row_str += str(piece)

            if empty_count > 0:
                row_str += str(empty_count)

            fen_rows.append(row_str)

        return "/".join(fen_rows)

    def _castling_to_fen(self) -> str:
        rights = ""
        if self.castling_rights.white_kingside:
            rights += "K"
        if self.castling_rights.white_queenside:
            rights += "Q"
        if self.castling_rights.black_kingside:
            rights += "k"
        if self.castling_rights.black_queenside:
            rights += "q"

        return rights if rights else "-"

    def _en_passant_to_fen(self) -> str:
        if self.en_passant_square is None:
            return "-"
        return self.en_passant_square.to_notation()

    def to_fen(self) -> str:
        board_part = self._board_to_fen()
        turn_part = "w" if self.side_to_move == Color.WHITE else "b"
        castling_part = self._castling_to_fen()
        en_passant_part = self._en_passant_to_fen()

        return (
            f"{board_part} {turn_part} {castling_part} {en_passant_part} "
            f"{self.halfmove_clock} {self.fullmove_number}"
        )
