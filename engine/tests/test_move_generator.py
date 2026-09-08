import pytest

from chess_engine.move import Move
from chess_engine.move_generator import MoveGenerator
from chess_engine.position import Position
from chess_engine.square import Square
from tests.conftest import CASTLING_FEN, EN_PASSANT_FEN, STARTING_FEN


@pytest.fixture
def generator():
    return MoveGenerator()


def test_pawn_single_and_double_push_from_e2(generator, starting_position):
    moves = generator.generate_moves_for_square(starting_position, Square.from_notation("e2"))
    ucis = {move.to_uci() for move in moves}
    assert "e2e3" in ucis
    assert "e2e4" in ucis


def test_knight_moves_from_b1(generator, starting_position):
    moves = generator.generate_moves_for_square(starting_position, Square.from_notation("b1"))
    ucis = {move.to_uci() for move in moves}
    assert ucis == {"b1a3", "b1c3"}


def test_king_moves_from_start(generator, starting_position):
    moves = generator.generate_moves_for_square(starting_position, Square.from_notation("e1"))
    assert moves == []


def test_castling_available_in_open_position(generator):
    position = Position.from_fen(CASTLING_FEN)
    moves = generator.generate_castling_moves(position)
    ucis = {move.to_uci() for move in moves}
    assert "e1g1" in ucis


def test_en_passant_generated(generator):
    position = Position.from_fen(EN_PASSANT_FEN)
    moves = generator.generate_moves_for_square(position, Square.from_notation("e5"))
    ucis = {move.to_uci() for move in moves}
    assert "e5d6" in ucis


def test_promotion_moves_generated(generator):
    position = Position.from_fen("8/P7/8/8/8/8/8/4K2k w - - 0 1")
    moves = generator.generate_moves_for_square(position, Square.from_notation("a7"))
    ucis = {move.to_uci() for move in moves}
    assert "a7a8q" in ucis
    assert "a7a8r" in ucis
    assert "a7a8b" in ucis
    assert "a7a8n" in ucis


def test_rook_slides_on_open_rank(generator):
    position = Position.from_fen("8/8/8/8/4R3/8/8/4K2k w - - 0 1")
    moves = generator.generate_moves_for_square(position, Square.from_notation("e4"))
    ucis = {move.to_uci() for move in moves}
    assert "e4a4" in ucis
    assert "e4h4" in ucis


def test_generate_all_moves_count_at_start(generator, starting_position):
    moves = generator.generate_all_moves(starting_position)
    assert len(moves) == 20


def test_empty_square_has_no_moves(generator, starting_position):
    assert generator.generate_moves_for_square(starting_position, Square.from_notation("e4")) == []


def test_opponent_piece_has_no_moves(generator, starting_position):
    assert generator.generate_moves_for_square(starting_position, Square.from_notation("e7")) == []


def test_is_pseudolegal_rejects_teleport(generator, starting_position):
    move = Move.from_uci("e2e5")
    assert not generator.is_pseudolegal(starting_position, move)


def test_is_pseudolegal_accepts_valid_pawn_push(generator, starting_position):
    move = Move.from_uci("e2e4")
    assert generator.is_pseudolegal(starting_position, move)
