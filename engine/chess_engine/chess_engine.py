from chess_engine.attack_detector import AttackDetector
from chess_engine.errors import IllegalMoveError
from chess_engine.move import Move
from chess_engine.move_generator import MoveGenerator
from chess_engine.move_validator import MoveValidator
from chess_engine.position import Position
from chess_engine.square import Square
from chess_engine.types import GameStatus


class ChessEngine:
    def __init__(self, position: Position | None = None) -> None:
        self.attack_detector = AttackDetector()
        self.generator = MoveGenerator(self.attack_detector)
        self.validator = MoveValidator(self.attack_detector, self.generator)
        self.position = position or Position.starting()

    def legal_moves(self, position: Position | None = None) -> list[Move]:
        position = position or self.position
        pseudolegal = self.generator.generate_all_moves(position)
        return self.validator.get_legal_moves(position, pseudolegal)

    def legal_moves_from_square(self, position: Position, square: str) -> list[Move]:
        square_obj = Square.from_notation(square)
        pseudolegal = self.generator.generate_moves_for_square(position, square_obj)
        return self.validator.get_legal_moves(position, pseudolegal)

    def game_status(self, position: Position | None = None) -> GameStatus:
        position = position or self.position
        side = position.side_to_move
        in_check = self.attack_detector.is_in_check(position, side)
        moves = self.legal_moves(position)
        if not moves:
            return GameStatus.CHECKMATE if in_check else GameStatus.STALEMATE

        return GameStatus.ONGOING

    def make_move(self, move: Move, position: Position | None = None) -> tuple[Position, GameStatus]:
        position = position or self.position

        if not self.validator.is_legal(position, move):
            raise IllegalMoveError("Move is illegal!")

        new_position = position.apply_move(move)
        self.position = new_position
        return new_position, self.game_status(new_position)
