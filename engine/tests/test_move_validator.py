import pytest

from chess_engine.attack_detector import AttackDetector
from chess_engine.move import Move
from chess_engine.move_generator import MoveGenerator
from chess_engine.move_validator import MoveValidator
from chess_engine.position import Position
from chess_engine.square import Square


@pytest.fixture
def validator():
    attack_detector = AttackDetector()
    generator = MoveGenerator(attack_detector)
    return MoveValidator(attack_detector, generator)


def test_starting_e2e4_is_legal(validator, starting_position):
    move = Move.from_uci("e2e4")
    assert validator.is_legal(starting_position, move)


from tests.conftest import CASTLING_THROUGH_CHECK_FEN, CHECK_FEN

#     pseudolegal = MoveGenerator(validator.attack_detector).generate_all_moves(position)
#     legal = validator.get_legal_moves(position, pseudolegal)
#     ucis = {move.to_uci() for move in legal}
#     assert "e8e7" not in ucis


def test_pinned_piece_cannot_move(validator):
    position = Position.from_fen("6k1/8/8/8/8/5b2/8/6K1 w - - 0 1")
    move = Move.from_uci("g1h1")
    assert not validator.is_legal(position, move)


def test_castling_through_check_is_illegal(validator):
    position = Position.from_fen(CASTLING_THROUGH_CHECK_FEN)
    move = Move(Square.from_notation("e1"), Square.from_notation("g1"), is_castling=True)
    assert not validator.is_legal(position, move)


def test_e2e5_is_not_legal(validator, starting_position):
    move = Move.from_uci("e2e5")
    assert not validator.is_legal(starting_position, move)


def test_moving_opponent_piece_is_not_legal(validator, starting_position):
    move = Move.from_uci("e7e5")
    assert not validator.is_legal(starting_position, move)


def test_moving_from_empty_square_is_not_legal(validator, starting_position):
    move = Move.from_uci("e4e5")
    assert not validator.is_legal(starting_position, move)
