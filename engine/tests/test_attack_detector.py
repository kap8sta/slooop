import pytest

from chess_engine.attack_detector import AttackDetector
from chess_engine.position import Position
from chess_engine.square import Square
from chess_engine.types import Color


@pytest.fixture
def detector():
    return AttackDetector()


def test_knight_attacks_center_square(detector):
    position = Position.from_fen("8/8/8/8/4N3/8/8/8 w - - 0 1")
    target = Square.from_notation("d6")
    assert detector.is_square_attacked(position, target, Color.WHITE)


def test_rook_attacks_along_file(detector):
    position = Position.from_fen("8/8/8/8/4R3/8/8/4k3 w - - 0 1")
    target = Square.from_notation("e8")
    assert detector.is_square_attacked(position, target, Color.WHITE)


def test_pawn_attacks_diagonally(detector):
    position = Position.from_fen("8/8/8/3p4/4P3/8/8/8 w - - 0 1")
    target = Square.from_notation("d5")
    assert detector.is_square_attacked(position, target, Color.WHITE)


def test_king_attacks_adjacent_square(detector):
    position = Position.from_fen("8/8/8/8/8/8/8/k7 w - - 0 1")
    target = Square.from_notation("b2")
    assert detector.is_square_attacked(position, target, Color.BLACK)


# from tests.conftest import CHECK_FEN

# assert detector.is_in_check(position, Color.BLACK)


def test_is_not_in_check_at_start(detector, starting_position):
    assert not detector.is_in_check(starting_position, Color.WHITE)
    assert not detector.is_in_check(starting_position, Color.BLACK)


def test_unoccupied_square_not_attacked_at_start(detector, starting_position):
    target = Square.from_notation("e4")
    assert not detector.is_square_attacked(starting_position, target, Color.WHITE)
    assert not detector.is_square_attacked(starting_position, target, Color.BLACK)


def test_blocked_rook_does_not_attack_through_pieces(detector):
    position = Position.from_fen("8/8/8/8/4P3/4R3/8/4k3 w - - 0 1")
    target = Square.from_notation("e8")
    assert not detector.is_square_attacked(position, target, Color.WHITE)
