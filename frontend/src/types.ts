export type PlayerColor = 'WHITE' | 'BLACK';

export type RoomState =
  | 'WAITING_FOR_OPPONENT'
  | 'ONGOING'
  | 'FINISHED'
  | 'CHECK'
  | 'CHECKMATE'
  | 'STALEMATE'
  | 'DRAW';

export type MatchResult = 'WHITE_WIN' | 'BLACK_WIN' | 'DRAW';

export interface UserLobbyDto {
  id?: number;
  username: string;
  color?: PlayerColor;
  Color?: PlayerColor;
}

export interface UserCreateDto {
  username: string;
  password: string;
}

export interface UserResponseDto {
  id: number;
  username: string;
  createdAt: string;
}

export interface Room {
  uuid: string;
  roomState: RoomState;
  firstPlayer?: UserLobbyDto;
  secondPlayer?: UserLobbyDto;
  currentFen?: string;
  activeColor?: PlayerColor;
  legal_moves?: Record<string, string[]>;
}

export interface MatchResponseDto {
  id: number;
  roomUuid: string;
  whitePlayer?: UserLobbyDto;
  blackPlayer?: UserLobbyDto;
  finalFen?: string;
  pgn?: string;
  result?: MatchResult;
}

export interface MoveDto {
  from: string;
  to: string;
  promotion?: string;
}

export interface WebSocketEvent<T> {
  type: string;
  payload: T;
}

export interface ChatMessageDto {
  message: string;
  username: string;
  time?: string;
}

export interface MakeMoveResponse {
  fen: string;
  side_to_move?: string;
  game_status?: string;
  legal_moves?: string[];
}

export interface GameOverDto {
  winner: string;
  reason: RoomState;
}
