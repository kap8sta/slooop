from app.schemas.chess import ApiGameStatus, LegalMovesResponse, MakeMoveResponse, StartNewGameResponse
from chess_engine.chess_engine import ChessEngine
from chess_engine.move import Move
from chess_engine.position import Position


class ChessService:
    def __init__(self) -> None:
        self.engine = ChessEngine()

    def start_new_game(self) -> StartNewGameResponse:
        position = Position.starting()
        game_status = self.engine.game_status(position)
        moves = self.engine.legal_moves(position)
        return StartNewGameResponse(
            fen=position.to_fen(),
            side_to_move=position.side_to_move.value,
            game_status=ApiGameStatus.from_domain(game_status),
            legal_moves=[move.to_uci() for move in moves],
        )

    def legal_moves(self, fen: str) -> LegalMovesResponse:
        position = Position.from_fen(fen)
        moves = self.engine.legal_moves(position)
        return [move.to_uci() for move in moves]

    def make_move(self, fen: str, move_str: str) -> MakeMoveResponse:
        position = Position.from_fen(fen)
        move = Move.from_uci(move_str)
        new_position, game_status = self.engine.make_move(move, position)

        moves = self.engine.legal_moves(new_position)

        return MakeMoveResponse(
            fen=new_position.to_fen(),
            side_to_move=new_position.side_to_move.value,
            game_status=ApiGameStatus.from_domain(game_status),
            legal_moves=[move.to_uci() for move in moves],
        )
