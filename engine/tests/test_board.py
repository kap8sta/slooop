import pytest

from chess_engine.board import Board
from chess_engine.square import Square
from chess_engine.types import Color, Piece


def test_print_board(capsys):
    board = Board.starting()
    board.print_board()
    captured = capsys.readouterr()
    assert "P" in captured.out
    assert "p" in captured.out


def test_startpos_white_pawn_on_e2():
    board = Board.starting()
    assert board[Square.from_notation("e2")] == Piece.WHITE_PAWN


def test_startpos_white_rook_on_h1():
    board = Board.starting()
    assert board[Square.from_notation("h1")] == Piece.WHITE_ROOK


def test_startpos_white_rook_on_a1():
    board = Board.starting()
    assert board[Square.from_notation("a1")] == Piece.WHITE_ROOK


def test_startpos_black_king_on_e8():
    board = Board.starting()
    assert board[Square.from_notation("e8")] == Piece.BLACK_KING


def test_startpos_black_rook_on_h8():
    board = Board.starting()
    assert board[Square.from_notation("h8")] == Piece.BLACK_ROOK


def test_startpos_black_rook_on_a8():
    board = Board.starting()
    assert board[Square.from_notation("a8")] == Piece.BLACK_ROOK


def test_empty_board_has_no_pieces():
    board = Board.empty()
    for _, piece in board.iter_pieces():
        assert piece == Piece.EMPTY


def test_copy_is_independent():
    board = Board.starting()
    copied = board.copy()
    copied.remove_piece(Square.from_notation("e2"))
    assert board[Square.from_notation("e2")] == Piece.WHITE_PAWN
    assert copied[Square.from_notation("e2")] == Piece.EMPTY


def test_move_piece():
    board = Board.starting()
    from_square = Square.from_notation("e2")
    to_square = Square.from_notation("e4")
    board.move_piece(from_square, to_square)
    assert board[from_square] == Piece.EMPTY
    assert board[to_square] == Piece.WHITE_PAWN


def test_find_king_white():
    board = Board.starting()
    assert board.find_king(Color.WHITE) == Square.from_notation("e1")


def test_find_king_black():
    board = Board.starting()
    assert board.find_king(Color.BLACK) == Square.from_notation("e8")


def test_default_constructor_is_starting_position():
    board = Board()
    assert board[Square.from_notation("e1")] == Piece.WHITE_KING


def test_find_king_raises_when_missing():
    board = Board.empty()
    with pytest.raises(ValueError, match="Король не найден"):
        board.find_king(Color.WHITE)
