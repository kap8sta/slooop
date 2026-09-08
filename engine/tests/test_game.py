import pytest

from chess_engine.chess_engine import ChessEngine
from chess_engine.move import Move
from chess_engine.position import Position
from chess_engine.types import Color, GameStatus
from tests.conftest import CHECK_FEN, CHECKMATE_FEN, EN_PASSANT_FEN, PRE_CHECKMATE_FEN, STALEMATE_FEN


def test_starting_position_has_20_legal_moves(engine):
    assert len(engine.legal_moves()) == 20


def test_legal_moves_from_e2(engine, starting_fen):
    position = Position.from_fen(starting_fen)
    moves = engine.legal_moves_from_square(position, "e2")
    ucis = {move.to_uci() for move in moves}
    assert ucis == {"e2e3", "e2e4"}


def test_make_move_e2e4(engine):
    move = Move.from_uci("e2e4")
    new_position, status = engine.make_move(move)
    assert new_position.side_to_move == Color.BLACK
    assert status == GameStatus.ONGOING
    assert new_position.board[Move.from_uci("e2e4").to_square].value == "P"


def test_play_move_returns_fen(engine, starting_fen):
    result = engine.play_move(starting_fen, "e2e4")
    assert result["status"] == "ongoing"
    assert result["winner"] is None
    assert "4P3" in result["fen"]


def test_position_fen_roundtrip(starting_fen):
    position = Position.from_fen(starting_fen)
    assert position.to_fen() == starting_fen


def test_move_uci_roundtrip():
    move = Move.from_uci("e7e8q")
    assert move.to_uci() == "e7e8q"
    assert Move.from_uci(move.to_uci()) == move


def test_game_status_check(engine):
    position = Position.from_fen(CHECK_FEN)
    assert engine.game_status(position) == GameStatus.CHECK


def test_game_status_checkmate(engine):
    position = Position.from_fen(CHECKMATE_FEN)
    assert engine.game_status(position) == GameStatus.CHECKMATE


def test_game_status_stalemate(engine):
    position = Position.from_fen(STALEMATE_FEN)
    assert engine.game_status(position) == GameStatus.STALEMATE


def test_play_move_checkmate_returns_winner(engine):
    result = engine.play_move(PRE_CHECKMATE_FEN, "f7g7")
    assert result["status"] == "checkmate"
    assert result["winner"] == "white"


def test_en_passant_is_legal(engine):
    position = Position.from_fen(EN_PASSANT_FEN)
    moves = engine.legal_moves_from_square(position, "e5")
    ucis = {move.to_uci() for move in moves}
    assert "e5d6" in ucis


def test_illegal_move_raises(engine):
    move = Move.from_uci("e2e5")
    with pytest.raises(ValueError, match="Нелегальный ход"):
        engine.make_move(move)


def test_play_move_rejects_illegal_uci(engine, starting_fen):
    with pytest.raises(ValueError, match="Нелегальный ход"):
        engine.play_move(starting_fen, "e2e5")


def test_cannot_move_opponent_piece(engine, starting_fen):
    position = Position.from_fen(starting_fen)
    moves = engine.legal_moves_from_square(position, "e7")
    assert moves == []
