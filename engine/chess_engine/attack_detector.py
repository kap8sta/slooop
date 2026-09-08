from chess_engine.position import Position
from chess_engine.square import Square
from chess_engine.types import (
    ALL_DIRECTIONS,
    DIAGONAL_DIRECTIONS,
    DOWN_LEFT,
    DOWN_RIGHT,
    KNIGHT_OFFSETS,
    ORTHOGONAL_DIRECTIONS,
    UP_LEFT,
    UP_RIGHT,
    Color,
    Piece,
    PieceType,
    Vector,
)


class AttackDetector:
    def _first_piece_along_ray(self, position: Position, square: Square, direction: Vector) -> Piece | None:
        current = square

        while True:
            current = current + direction
            if not current.is_valid:
                return None
            piece = position.board[current]
            if piece.piece_type != PieceType.EMPTY:
                return piece

    def _is_attacked_by_knight(self, position: Position, square: Square, enemy_color: Color) -> bool:
        for offset in KNIGHT_OFFSETS:
            target = square + offset
            if not target.is_valid:
                continue
            piece = position.board[target]
            if piece.piece_type == PieceType.KNIGHT and piece.piece_color == enemy_color:
                return True

        return False

    def _is_attacked_by_sliding_moves(
        self,
        position: Position,
        square: Square,
        enemy_color: Color,
    ) -> bool:
        for direction in ORTHOGONAL_DIRECTIONS:
            piece = self._first_piece_along_ray(position, square, direction)
            if (
                piece is not None
                and piece.piece_color == enemy_color
                and piece.piece_type in (PieceType.ROOK, PieceType.QUEEN)
            ):
                return True

        for direction in DIAGONAL_DIRECTIONS:
            piece = self._first_piece_along_ray(position, square, direction)
            if (
                piece is not None
                and piece.piece_color == enemy_color
                and piece.piece_type in (PieceType.BISHOP, PieceType.QUEEN)
            ):
                return True

        return False

    def _is_attacked_by_pawn(self, position: Position, square: Square, enemy_color: Color) -> bool:
        if enemy_color == Color.BLACK:
            directions = UP_LEFT, UP_RIGHT
        else:
            directions = DOWN_LEFT, DOWN_RIGHT

        for direction in directions:
            target = square + direction
            if not target.is_valid:
                continue
            piece = position.board[target]
            if piece.piece_type == PieceType.PAWN and piece.piece_color == enemy_color:
                return True

        return False

    def _is_attacked_by_king(self, position: Position, square: Square, enemy_color: Color) -> bool:
        for direction in ALL_DIRECTIONS:
            target = square + direction
            if not target.is_valid:
                continue
            piece = position.board[target]
            if piece.piece_type == PieceType.KING and piece.piece_color == enemy_color:
                return True

        return False

    def is_square_attacked(self, position: Position, square: Square, enemy_color: Color) -> bool:
        return (
            self._is_attacked_by_king(position, square, enemy_color)
            or self._is_attacked_by_knight(position, square, enemy_color)
            or self._is_attacked_by_pawn(position, square, enemy_color)
            or self._is_attacked_by_sliding_moves(position, square, enemy_color)
        )

    def is_in_check(self, position: Position, color: Color) -> bool:
        enemy_color = Color.BLACK if color == Color.WHITE else Color.WHITE
        king_square = position.board.find_king(color)
        return self.is_square_attacked(position, king_square, enemy_color)
