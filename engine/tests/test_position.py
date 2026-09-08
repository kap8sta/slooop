import pytest

from chess_engine.move import Move
from chess_engine.position import Position
from chess_engine.square import Square
from chess_engine.types import Color, Piece
from tests.conftest import CASTLING_FEN, EN_PASSANT_FEN, STARTING_FEN


def test_starting_position_side_to_move(starting_position):
    assert starting_position.side_to_move == Color.WHITE
    assert starting_position.fullmove_number == 1
    assert starting_position.halfmove_clock == 0
    assert starting_position.en_passant_square is None


def test_starting_position_castling_rights(starting_position):
    rights = starting_position.castling_rights
    assert rights.white_kingside
    assert rights.white_queenside
    assert rights.black_kingside
    assert rights.black_queenside


def test_copy_does_not_share_board(starting_position):
    copied = starting_position.copy()
    copied.board.remove_piece(Square.from_notation("e2"))
    assert starting_position.board[Square.from_notation("e2")] == Piece.WHITE_PAWN


def test_fen_roundtrip(starting_position):
    assert starting_position.to_fen() == STARTING_FEN


def test_from_fen_matches_starting(starting_fen):
    position = Position.from_fen(starting_fen)
    assert position.to_fen() == starting_fen


def test_apply_move_changes_side_to_move(starting_position):
    move = Move.from_uci("e2e4")
    new_position = starting_position.apply_move(move)
    assert new_position.side_to_move == Color.BLACK
    assert new_position.board[Square.from_notation("e4")] == Piece.WHITE_PAWN
    assert new_position.board[Square.from_notation("e2")] == Piece.EMPTY


def test_apply_move_sets_en_passant_square(starting_position):
    position = starting_position
    position = position.apply_move(Move.from_uci("e2e4"))
    position = position.apply_move(Move.from_uci("a7a6"))
    position = position.apply_move(Move.from_uci("e4e5"))
    position = position.apply_move(Move.from_uci("d7d5"))
    assert position.en_passant_square == Square.from_notation("d6")


def test_apply_en_passant_capture():
    position = Position.from_fen(EN_PASSANT_FEN)
    new_position = position.apply_move(Move.from_uci("e5d6"))
    assert new_position.board[Square.from_notation("d6")] == Piece.WHITE_PAWN
    assert new_position.board[Square.from_notation("d5")] == Piece.EMPTY
    assert new_position.board[Square.from_notation("e5")] == Piece.EMPTY


def test_apply_move_updates_halfmove_and_fullmove(starting_position):
    after_e4 = starting_position.apply_move(Move.from_uci("e2e4"))
    assert after_e4.halfmove_clock == 0
    assert after_e4.fullmove_number == 1

    after_e4_e5 = after_e4.apply_move(Move.from_uci("e7e5"))
    assert after_e4_e5.halfmove_clock == 0
    assert after_e4_e5.fullmove_number == 2

    after_e4_e5_nf3 = after_e4_e5.apply_move(Move.from_uci("g1f3"))
    assert after_e4_e5_nf3.halfmove_clock == 1
    assert after_e4_e5_nf3.fullmove_number == 2


def test_apply_castling_moves_rook():
    position = Position.from_fen(CASTLING_FEN)
    move = Move(
        Square.from_notation("e1"),
        Square.from_notation("g1"),
        is_castling=True,
    )
    new_position = position.apply_move(move)
    assert new_position.board[Square.from_notation("g1")] == Piece.WHITE_KING
    assert new_position.board[Square.from_notation("f1")] == Piece.WHITE_ROOK
    assert new_position.board[Square.from_notation("e1")] == Piece.EMPTY
    assert new_position.board[Square.from_notation("h1")] == Piece.EMPTY


def test_apply_promotion():
    position = Position.from_fen("8/P7/8/8/8/8/8/4K2k w - - 0 1")
    new_position = position.apply_move(Move.from_uci("a7a8q"))
    assert new_position.board[Square.from_notation("a8")] == Piece.WHITE_QUEEN


def test_castling_rights_removed_after_king_move():
    position = Position.from_fen(CASTLING_FEN)
    move = Move(
        Square.from_notation("e1"),
        Square.from_notation("g1"),
        is_castling=True,
    )
    new_position = position.apply_move(move)
    assert not new_position.castling_rights.white_kingside
    assert not new_position.castling_rights.white_queenside


def test_from_fen_invalid_format():
    with pytest.raises(ValueError, match="Неверный формат FEN"):
        Position.from_fen("only-three-parts")
