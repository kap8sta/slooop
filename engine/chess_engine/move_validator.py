from chess_engine.attack_detector import AttackDetector
from chess_engine.move import Move
from chess_engine.move_generator import MoveGenerator
from chess_engine.position import Position
from chess_engine.types import Color


class MoveValidator:
    def __init__(
        self,
        attack_detector: AttackDetector | None = None,
        move_generator: MoveGenerator | None = None,
    ) -> None:
        self.attack_detector = attack_detector or AttackDetector()
        self.move_generator = move_generator

    def is_legal(self, position: Position, move: Move) -> bool:
        if self.move_generator is not None and not self.move_generator.is_pseudolegal(position, move):
            return False

        moving_color = position.side_to_move
        enemy_color = Color.BLACK if moving_color == Color.WHITE else Color.WHITE

        new_position = position.apply_move(move)
        king_square = new_position.board.find_king(moving_color)
        return not self.attack_detector.is_square_attacked(new_position, king_square, enemy_color)

    def get_legal_moves(self, position: Position, pseudolegal_moves: list[Move]) -> list[Move]:
        return [move for move in pseudolegal_moves if self.is_legal(position, move)]
