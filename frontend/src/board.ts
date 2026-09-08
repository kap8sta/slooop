const UNICODE: Record<string, string> = {
  wK: '♔',
  wQ: '♕',
  wR: '♖',
  wB: '♗',
  wN: '♘',
  wP: '♙',
  bK: '♚',
  bQ: '♛',
  bR: '♜',
  bB: '♝',
  bN: '♞',
  bP: '♟',
};

const FILES = 'abcdefgh';

export type BoardHandlers = {
  onSquare: (square: string) => void;
};

export class ChessBoardView {
  private root: HTMLElement;
  private orientation: 'white' | 'black' = 'white';
  private pieces = new Map<string, string>();
  private selected: string | null = null;
  private targets = new Set<string>();
  private lastMove: { from: string; to: string } | null = null;
  private handlers: BoardHandlers;

  constructor(root: HTMLElement, handlers: BoardHandlers) {
    this.root = root;
    this.handlers = handlers;
    this.render();
  }

  setOrientation(color: 'white' | 'black') {
    this.orientation = color;
    this.render();
  }

  setPositionFromFen(fen: string) {
    this.pieces.clear();
    const boardPart = fen.split(' ')[0] || '';
    let rank = 8;
    let file = 0;
    for (const ch of boardPart) {
      if (ch === '/') {
        rank -= 1;
        file = 0;
        continue;
      }
      if (ch >= '1' && ch <= '8') {
        file += Number(ch);
        continue;
      }
      const isWhite = ch === ch.toUpperCase();
      const type = ch.toUpperCase();
      const map: Record<string, string> = { K: 'K', Q: 'Q', R: 'R', B: 'B', N: 'N', P: 'P' };
      const piece = `${isWhite ? 'w' : 'b'}${map[type] || ''}`;
      const square = `${FILES[file]}${rank}`;
      this.pieces.set(square, piece);
      file += 1;
    }
    this.render();
  }

  setSelection(selected: string | null, targets: string[] = []) {
    this.selected = selected;
    this.targets = new Set(targets);
    this.render();
  }

  setLastMove(from: string | null, to: string | null) {
    this.lastMove = from && to ? { from, to } : null;
    this.render();
  }

  private render() {
    this.root.replaceChildren();
    const ranks = this.orientation === 'white' ? [8, 7, 6, 5, 4, 3, 2, 1] : [1, 2, 3, 4, 5, 6, 7, 8];
    const files = this.orientation === 'white' ? FILES.split('') : FILES.split('').reverse();

    for (const rank of ranks) {
      for (const file of files) {
        const square = `${file}${rank}`;
        const light = (FILES.indexOf(file) + rank) % 2 === 1;
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = `sq ${light ? 'light' : 'dark'}`;
        btn.dataset.square = square;
        if (this.selected === square) btn.classList.add('selected');
        if (this.targets.has(square)) btn.classList.add('target');
        if (this.lastMove && (this.lastMove.from === square || this.lastMove.to === square)) {
          btn.classList.add('last');
        }
        const piece = this.pieces.get(square);
        if (piece) {
          btn.textContent = UNICODE[piece] || '';
          btn.classList.add(piece.startsWith('w') ? 'white-piece' : 'black-piece');
        }
        btn.addEventListener('click', () => this.handlers.onSquare(square));
        this.root.appendChild(btn);
      }
    }
  }
}

export function askPromotion(): Promise<string | null> {
  const host = document.getElementById('promotion');
  if (!host) return Promise.resolve('q');
  return new Promise((resolve) => {
    host.classList.remove('hidden');
    host.replaceChildren();
    const title = document.createElement('p');
    title.textContent = 'Превращение пешки';
    host.appendChild(title);
    const row = document.createElement('div');
    row.className = 'row';
    const choices: Array<[string, string]> = [
      ['q', 'Ферзь'],
      ['r', 'Ладья'],
      ['b', 'Слон'],
      ['n', 'Конь'],
    ];
    for (const [code, label] of choices) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'btn primary';
      btn.textContent = label;
      btn.addEventListener('click', () => {
        host.classList.add('hidden');
        host.replaceChildren();
        resolve(code);
      });
      row.appendChild(btn);
    }
    const cancel = document.createElement('button');
    cancel.type = 'button';
    cancel.className = 'btn';
    cancel.textContent = 'Отмена';
    cancel.addEventListener('click', () => {
      host.classList.add('hidden');
      host.replaceChildren();
      resolve(null);
    });
    host.append(row, cancel);
  });
}
