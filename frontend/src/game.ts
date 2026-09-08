import { Client } from '@stomp/stompjs';
import { Chess } from 'chess.js';
import { askPromotion, ChessBoardView } from './board';
import type {
  ChatMessageDto,
  GameOverDto,
  MakeMoveResponse,
  MoveDto,
  PlayerColor,
  Room,
  UserLobbyDto,
  UserResponseDto,
  WebSocketEvent,
} from './types';

const START_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';

let toast: (msg: string) => void = () => {};
let me: UserResponseDto | null = null;
let client: Client | null = null;
let roomUuid: string | null = null;
let room: Room | null = null;
let board: ChessBoardView | null = null;
let chess = new Chess();
let selected: string | null = null;
let joining = false;
let chatReady = false;

export function setToast(fn: (msg: string) => void) {
  toast = fn;
}

export function setMe(user: UserResponseDto | null) {
  me = user;
}

export function disconnectGame() {
  if (client) {
    client.deactivate();
    client = null;
  }
  roomUuid = null;
  room = null;
  selected = null;
  joining = false;
}

export async function openGame(uuid: string) {
  roomUuid = uuid;
  selected = null;
  chess = new Chess();
  const boardEl = document.getElementById('board');
  if (boardEl && !board) {
    board = new ChessBoardView(boardEl, { onSquare: onSquare });
  }
  const uuidEl = document.getElementById('active-room-uuid');
  if (uuidEl) uuidEl.textContent = uuid;
  initChat();
  clearChat();
  renderMoves([]);
  connectWs(uuid);
}

function playerColor(player?: UserLobbyDto | null): PlayerColor | null {
  if (!player) return null;
  const raw = player.color || player.Color;
  if (raw === 'WHITE' || raw === 'BLACK') return raw;
  return null;
}

function myColor(): PlayerColor | null {
  if (!room || !me) return null;
  const uid = String(me.id);
  const name = me.username.trim().toLowerCase();
  const match = (p?: UserLobbyDto) => {
    if (!p) return false;
    if (p.id != null && String(p.id) === uid) return true;
    return (p.username || '').trim().toLowerCase() === name;
  };
  if (match(room.firstPlayer)) return playerColor(room.firstPlayer);
  if (match(room.secondPlayer)) return playerColor(room.secondPlayer);
  return null;
}

function iAmPlayer(): boolean {
  if (!room || !me) return false;
  const uid = String(me.id);
  return [room.firstPlayer, room.secondPlayer].some((p) => p && String(p.id) === uid);
}

async function tryJoinIfNeeded() {
  if (!room || !roomUuid || !me || joining) return;
  if (iAmPlayer()) return;
  if (room.roomState !== 'WAITING_FOR_OPPONENT' || room.secondPlayer) return;
  joining = true;
  try {
    const res = await fetch(`/api/rooms/${roomUuid}`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!res.ok && res.status !== 409) {
      const text = await res.text();
      toast(text || 'Не удалось присоединиться');
    }
  } catch {
    toast('Не удалось присоединиться к комнате');
  } finally {
    joining = false;
  }
}

function applyFen(fen: string) {
  try {
    chess.load(fen);
  } catch {
    chess = new Chess(START_FEN);
  }
  board?.setPositionFromFen(chess.fen());
}

function applyRoom(next: Room) {
  room = next;
  if (next.currentFen) applyFen(next.currentFen);
  else applyFen(START_FEN);

  const color = myColor();
  board?.setOrientation(color === 'BLACK' ? 'black' : 'white');
  updateStatus();
  updatePlayers();
  selected = null;
  board?.setSelection(null);
  void tryJoinIfNeeded();
}

function updateStatus() {
  const el = document.getElementById('game-status');
  const turn = document.getElementById('turn-text');
  if (!el) return;
  if (!room) {
    el.textContent = 'Подключение…';
    return;
  }
  const map: Record<string, string> = {
    WAITING_FOR_OPPONENT: 'Ожидание соперника',
    ONGOING: 'Партия идёт',
    CHECK: 'Шах',
    CHECKMATE: 'Мат',
    STALEMATE: 'Пат',
    DRAW: 'Ничья',
    FINISHED: 'Партия окончена',
  };
  el.textContent = map[room.roomState] || room.roomState;
  if (turn) {
    const active = room.activeColor || (chess.turn() === 'w' ? 'WHITE' : 'BLACK');
    turn.textContent = active === 'WHITE' ? 'Ход белых' : 'Ход чёрных';
  }
}

function updatePlayers() {
  const color = myColor();
  const white = pick('WHITE');
  const black = pick('BLACK');
  const iAmBlack = color === 'BLACK';
  const top = iAmBlack ? white : black;
  const bottom = iAmBlack ? black : white;
  setPlayer('top', top?.username || 'Ожидание соперника', iAmBlack ? 'белые' : 'чёрные');
  setPlayer('bottom', bottom?.username || me?.username || 'Вы', iAmBlack ? 'чёрные' : 'белые');
}

function pick(color: PlayerColor): UserLobbyDto | undefined {
  if (!room) return undefined;
  if (playerColor(room.firstPlayer) === color) return room.firstPlayer;
  if (playerColor(room.secondPlayer) === color) return room.secondPlayer;
  return undefined;
}

function setPlayer(side: 'top' | 'bottom', name: string, colorLabel: string) {
  const nameEl = document.getElementById(`${side}-player-name`);
  const colorEl = document.getElementById(`${side}-player-color`);
  if (nameEl) nameEl.textContent = name;
  if (colorEl) colorEl.textContent = colorLabel;
}

function renderMoves(moves: MoveDto[]) {
  const list = document.getElementById('moves-list');
  if (!list) return;
  list.replaceChildren();
  if (!moves.length) {
    const empty = document.createElement('li');
    empty.className = 'muted';
    empty.textContent = 'Ходов пока нет';
    list.appendChild(empty);
    return;
  }
  for (let i = 0; i < moves.length; i += 2) {
    const li = document.createElement('li');
    const w = moves[i];
    const b = moves[i + 1];
    const fmt = (m?: MoveDto) => (m ? `${m.from}–${m.to}${m.promotion ? '=' + m.promotion.toUpperCase() : ''}` : '');
    li.textContent = `${Math.floor(i / 2) + 1}. ${fmt(w)} ${fmt(b)}`.trim();
    list.appendChild(li);
  }
  list.scrollTop = list.scrollHeight;
  const last = moves[moves.length - 1];
  if (last) board?.setLastMove(last.from, last.to);
}

function applyMoves(moves: MoveDto[]) {
  chess.reset();
  for (const move of moves) {
    try {
      chess.move({ from: move.from, to: move.to, promotion: move.promotion || undefined });
    } catch {
      /* ход уже проверен сервером; битая запись пропускаем */
    }
  }
  board?.setPositionFromFen(chess.fen());
  if (room) {
    room.activeColor = chess.turn() === 'w' ? 'WHITE' : 'BLACK';
    if (room.roomState === 'WAITING_FOR_OPPONENT' && moves.length) {
      room.roomState = 'ONGOING';
    }
    room.currentFen = chess.fen();
  }
  updateStatus();
  renderMoves(moves);
}

function canMove(): boolean {
  if (!room) return false;
  if (room.roomState !== 'ONGOING' && room.roomState !== 'CHECK') return false;
  const color = myColor();
  if (!color) return false;
  const active = room.activeColor || (chess.turn() === 'w' ? 'WHITE' : 'BLACK');
  return active === color;
}

async function onSquare(square: string) {
  if (!canMove()) return;
  const piece = chess.get(square as any);
  const myPrefix = myColor() === 'WHITE' ? 'w' : 'b';

  if (!selected) {
    if (!piece || piece.color !== myPrefix[0]) return;
    selected = square;
    const targets = chess.moves({ square: square as any, verbose: true }).map((m) => m.to);
    board?.setSelection(square, targets);
    return;
  }

  if (selected === square) {
    selected = null;
    board?.setSelection(null);
    return;
  }

  const from = selected;
  const moving = chess.get(from as any);
  let promotion: string | undefined;
  if (moving?.type === 'p' && (square.endsWith('8') || square.endsWith('1'))) {
    const choice = await askPromotion();
    if (!choice) return;
    promotion = choice;
  }

  const trial = chess.move({ from, to: square, promotion });
  if (!trial) {
    if (piece && piece.color === myPrefix[0]) {
      selected = square;
      const targets = chess.moves({ square: square as any, verbose: true }).map((m) => m.to);
      board?.setSelection(square, targets);
    }
    return;
  }
  chess.undo();
  selected = null;
  board?.setSelection(null);
  sendMove(from, square, promotion);
}

function sendMove(from: string, to: string, promotion?: string) {
  if (!client?.connected || !roomUuid) {
    toast('Нет соединения с сервером');
    return;
  }
  const payload: MoveDto = { from, to };
  if (promotion) payload.promotion = promotion;
  client.publish({
    destination: `/app/rooms/${roomUuid}/move`,
    body: JSON.stringify(payload),
  });
}

function connectWs(uuid: string) {
  if (client) {
    client.deactivate();
    client = null;
  }
  const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
  client = new Client({
    brokerURL: `${proto}//${location.host}/ws`,
    reconnectDelay: 2000,
    onConnect: () => {
      client?.subscribe(`/topic/rooms/${uuid}`, (message) => {
        try {
          const event = JSON.parse(message.body) as WebSocketEvent<unknown>;
          handleEvent(event);
        } catch (err) {
          console.error(err);
        }
      });
    },
    onStompError: () => toast('Ошибка игрового соединения'),
    onWebSocketError: () => toast('Не удалось открыть WebSocket'),
  });
  client.activate();
}

function handleEvent(event: WebSocketEvent<unknown>) {
  const type = event.type;
  const payload = event.payload;
  if ((type === 'MESSAGE' || type === 'CHAT_MESSAGE') && payload) {
    appendChat(payload as ChatMessageDto);
    return;
  }
  if (type === 'MATCH_MOVES' && Array.isArray(payload)) {
    applyMoves(payload as MoveDto[]);
    return;
  }
  if (type === 'MOVE' && payload && typeof payload === 'object') {
    const move = payload as MakeMoveResponse;
    if (move.fen) applyFen(move.fen);
    if (room) {
      room.currentFen = move.fen || room.currentFen;
      if (move.side_to_move === 'white') room.activeColor = 'WHITE';
      if (move.side_to_move === 'black') room.activeColor = 'BLACK';
      if (move.game_status === 'checkmate') room.roomState = 'CHECKMATE';
      if (move.game_status === 'stalemate') room.roomState = 'STALEMATE';
      if (move.game_status === 'draw') room.roomState = 'DRAW';
    }
    updateStatus();
    return;
  }
  if (type === 'ROOM_INFO' && payload && typeof payload === 'object') {
    applyRoom(payload as Room);
    return;
  }
  if (type === 'GAME_OVER' && payload && typeof payload === 'object') {
    const over = payload as GameOverDto;
    toast(`Игра окончена. Победитель: ${over.winner || '—'}`);
    if (room) room.roomState = over.reason || room.roomState;
    updateStatus();
  }
}

function initChat() {
  if (chatReady) return;
  const form = document.getElementById('chat-form');
  const input = document.getElementById('chat-input') as HTMLInputElement | null;
  form?.addEventListener('submit', (e) => {
    e.preventDefault();
    const text = input?.value.trim();
    if (!text) return;
    if (!client?.connected || !roomUuid) {
      toast('Чат недоступен');
      return;
    }
    client.publish({
      destination: `/app/rooms/${roomUuid}/message`,
      body: JSON.stringify({ message: text }),
    });
    if (input) input.value = '';
  });
  chatReady = true;
}

function clearChat() {
  document.getElementById('chat-messages')?.replaceChildren();
}

function appendChat(msg: ChatMessageDto) {
  const box = document.getElementById('chat-messages');
  if (!box) return;
  const mine = me && msg.username === me.username;
  const row = document.createElement('div');
  row.className = `msg${mine ? ' mine' : ''}`;
  const who = document.createElement('strong');
  who.textContent = mine ? 'Вы' : msg.username || 'Игрок';
  const text = document.createElement('span');
  text.textContent = msg.message;
  row.append(who, text);
  box.appendChild(row);
  box.scrollTop = box.scrollHeight;
}
