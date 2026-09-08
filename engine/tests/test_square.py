import pytest

from chess_engine.square import Square
from chess_engine.types import DOWN, UP, UP_LEFT


def test_to_notation():
    assert Square(4, 4).to_notation() == "e4"


def test_from_notation():
    assert Square.from_notation("e4").to_notation() == "e4"


def test_from_string_alias():
    assert Square.from_string("a1") == Square.from_notation("a1")


def test_corners_notation():
    assert Square.from_notation("a1").to_notation() == "a1"
    assert Square.from_notation("h8").to_notation() == "h8"


def test_is_valid_on_board():
    assert Square(0, 0).is_valid
    assert Square(7, 7).is_valid
    assert Square(3, 4).is_valid


def test_add_vector():
    square = Square(4, 4)
    assert square + UP == Square(3, 4)
    assert square + DOWN == Square(5, 4)
    assert square + UP_LEFT == Square(3, 3)


@pytest.mark.parametrize(
    ("row", "col"),
    [
        (-1, 0),
        (8, 0),
        (0, -1),
        (0, 8),
    ],
)
def test_is_valid_outside_board(row, col):
    assert not Square(row, col).is_valid
