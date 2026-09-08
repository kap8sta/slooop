from chess_engine.attack_detector import AttackDetector
from chess_engine.move import Move
from chess_engine.position import Position
from chess_engine.square import Square
from chess_engine.types import (
    ALL_DIRECTIONS,
    BLACK_HOME_RANK,
    BLACK_PAWN_RANK,
    DIAGONAL_DIRECTIONS,
    DOWN,
    DOWN_LEFT,
    DOWN_RIGHT,
    KNIGHT_OFFSETS,
    ORTHOGONAL_DIRECTIONS,
    PROMOTION_PIECES,
    UP,
    UP_LEFT,
    UP_RIGHT,
    WHITE_HOME_RANK,
    WHITE_PAWN_RANK,
    Color,
    PieceType,
    Vector,
)


class MoveGenerator:
    def __init__(self, attack_detector: AttackDetector | None = None) -> None:
        self.attack_detector = attack_detector or AttackDetector()
        self._piece_generators = {
            PieceType.PAWN: self.generate_pawn_moves,
            PieceType.KNIGHT: self.generate_knight_moves,
            PieceType.BISHOP: self.generate_sliding_moves,
            PieceType.QUEEN: self.generate_sliding_moves,
            PieceType.ROOK: self.generate_sliding_moves,
            PieceType.KING: self.generate_king_moves,
        }

    @staticmethod
    def _sliding_directions(piece_type: PieceType) -> list[Vector]:
        match piece_type:
            case PieceType.BISHOP:
                return DIAGONAL_DIRECTIONS
            case PieceType.QUEEN:
                return ALL_DIRECTIONS
            case PieceType.ROOK:
                return ORTHOGONAL_DIRECTIONS

    def _try_step(
        self,
        position: Position,
        from_square: Square,
        to_square: Square,
        moves: list[Move],
    ) -> bool:
        if not to_square.is_valid:
            return False

        target = position.board[to_square]

        if target.piece_type == PieceType.EMPTY:
            moves.append(Move(from_square=from_square, to_square=to_square))
            return True

        if target.piece_color != position.side_to_move and target.piece_type != PieceType.KING:
            moves.append(Move(from_square=from_square, to_square=to_square))

        return False

    def _add_pawn_move(
        self, from_square: Square, to_square: Square, color: Color, moves: list[Move], is_en_passant: bool = False
    ) -> bool:
        if not to_square.is_valid:
            return False

        is_promotion = (color == Color.WHITE and to_square.row == BLACK_HOME_RANK) or (
            color == Color.BLACK and to_square.row == WHITE_HOME_RANK
        )
        if is_promotion:
            for piece in PROMOTION_PIECES:
                moves.append(Move(from_square, to_square, piece))
        else:
            moves.append(Move(from_square, to_square, is_en_passant=is_en_passant))

        return True

    def _generate_pawn_forward_moves(self, position: Position, square: Square, color: Color) -> list[Move]:
        moves = []

        if color == Color.WHITE:
            direction = UP
            start_rank = WHITE_PAWN_RANK
        else:
            direction = DOWN
            start_rank = BLACK_PAWN_RANK

        target = square + direction
        if target.is_valid and position.board[target].piece_type == PieceType.EMPTY:
            self._add_pawn_move(square, target, color, moves)

            if square.row == start_rank:
                double_target = target + direction
                if (
                    double_target.is_valid
                    and position.board[double_target].piece_type == PieceType.EMPTY
                ):
                    self._add_pawn_move(square, double_target, color, moves)

        return moves

    def _generate_pawn_attack_moves(self, position: Position, square: Square, color: Color) -> list[Move]:
        moves = []

        if color == Color.WHITE:
            attack_directions = [UP_LEFT, UP_RIGHT]
        else:
            attack_directions = [DOWN_LEFT, DOWN_RIGHT]

        for direction in attack_directions:
            target = square + direction
            if not target.is_valid:
                continue

            if target == position.en_passant_square:
                self._add_pawn_move(square, target, color, moves, is_en_passant=True)
                continue

            target_piece = position.board[target]
            if not target_piece.is_empty and target_piece.piece_color != position.side_to_move:
                self._add_pawn_move(square, target, color, moves)

        return moves

    def generate_pawn_moves(self, position: Position, square: Square) -> list[Move]:
        moves = []
        piece = position.board[square]
        color = piece.piece_color
        moves.extend(self._generate_pawn_forward_moves(position, square, color))
        moves.extend(self._generate_pawn_attack_moves(position, square, color))

        return moves

    def generate_knight_moves(self, position: Position, square: Square) -> list[Move]:
        moves = []
        for offset in KNIGHT_OFFSETS:
            candidate = square + offset
            self._try_step(position, square, candidate, moves)

        return moves

    def generate_king_moves(self, position: Position, square: Square) -> list[Move]:
        moves = []
        for direction in ALL_DIRECTIONS:
            candidate = square + direction
            self._try_step(position, square, candidate, moves)

        return moves

    def generate_castling_moves(self, position: Position) -> list[Move]:
        moves = []
        color = position.side_to_move
        rank = WHITE_HOME_RANK if color == Color.WHITE else BLACK_HOME_RANK
        king_square = Square(rank, 4)
        enemy_color = Color.BLACK if color == Color.WHITE else Color.WHITE

        if position.castling_rights.kingside(color):
            between = [Square(rank, 5), Square(rank, 6)]
            if all(position.board[s].is_empty for s in between):
                crossed = [Square(rank, 4), Square(rank, 5), Square(rank, 6)]
                if not any(self.attack_detector.is_square_attacked(position, s, enemy_color) for s in crossed):
                    moves.append(Move(king_square, Square(rank, 6), is_castling=True))

        if position.castling_rights.queenside(color):
            between = [Square(rank, 1), Square(rank, 2), Square(rank, 3)]
            if all(position.board[s].is_empty for s in between):
                crossed = [Square(rank, 4), Square(rank, 3), Square(rank, 2)]
                if not any(self.attack_detector.is_square_attacked(position, s, enemy_color) for s in crossed):
                    moves.append(Move(king_square, Square(rank, 2), is_castling=True))

        return moves

    def generate_sliding_moves(self, position: Position, square: Square) -> list[Move]:
        piece = position.board[square]
        moves = []
        directions = self._sliding_directions(piece.piece_type)

        for direction in directions:
            current = square
            while True:
                current = current + direction
                if not self._try_step(position, square, current, moves):
                    break
        return moves

    def generate_moves_for_square(self, position: Position, square: Square) -> list[Move]:
        piece = position.board[square]
        if piece.is_empty or piece.piece_color != position.side_to_move:
            return []

        generator = self._piece_generators.get(piece.piece_type)
        if generator is None:
            return []

        moves = generator(position, square)
        if piece.piece_type == PieceType.KING:
            moves.extend(self.generate_castling_moves(position))
        return moves

    def generate_all_moves(self, position: Position) -> list[Move]:
        moves = []
        for square, piece in position.board.iter_pieces():
            if piece.piece_color != position.side_to_move:
                continue
            generator = self._piece_generators[piece.piece_type]
            moves.extend(generator(position, square))

        moves.extend(self.generate_castling_moves(position))
        return moves

    def is_pseudolegal(self, position: Position, move: Move) -> bool:
        piece = position.board[move.from_square]
        if piece.is_empty or piece.piece_color != position.side_to_move:
            return False

        candidates = self.generate_moves_for_square(position, move.from_square)
        if move.is_castling:
            candidates.extend(self.generate_castling_moves(position))

        return move in candidates
