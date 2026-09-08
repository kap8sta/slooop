import { apiFetch, fetchMe } from './api';
import { disconnectGame, openGame, setMe, setToast } from './game';
import type { MatchResponseDto, Room, UserCreateDto, UserResponseDto } from './types';

const authSection = document.getElementById('auth-section')!;
const lobbySection = document.getElementById('lobby-section')!;
const gameSection = document.getElementById('game-section')!;
const profileSection = document.getElementById('profile-section')!;
const toastEl = document.getElementById('status-message')!;
const usernameInput = document.getElementById('username') as HTMLInputElement;
const passwordInput = document.getElementById('password') as HTMLInputElement;
const roomUuidInput = document.getElementById('room-uuid') as HTMLInputElement;

let currentUser: UserResponseDto | null = null;
let viewedProfileId: number | null = null;

function showToast(msg: string) {
  toastEl.textContent = msg;
  toastEl.classList.remove('hidden');
  window.setTimeout(() => toastEl.classList.add('hidden'), 3500);
}

setToast(showToast);

function show(section: HTMLElement) {
  [authSection, lobbySection, gameSection, profileSection].forEach((el) => el.classList.add('hidden'));
  section.classList.remove('hidden');
}

function parseRoute() {
  const hash = window.location.hash || '#auth';
  const [route, param] = hash.split('/');
  return { route, param: param || null };
}

async function refreshSession(): Promise<boolean> {
  currentUser = await fetchMe();
  setMe(currentUser);
  const lobbyUser = document.getElementById('lobby-user');
  if (lobbyUser) {
    lobbyUser.textContent = currentUser
      ? `${currentUser.username}${currentUser.id < 0 ? ' (гость)' : ` · id ${currentUser.id}`}`
      : '';
  }
  return currentUser !== null;
}

async function route() {
  const { route, param } = parseRoute();
  const signedIn = currentUser !== null || (await refreshSession());

  if (!signedIn && route !== '#auth') {
    window.location.hash = '#auth';
    show(authSection);
    return;
  }
  if (signedIn && (route === '#auth' || route === '')) {
    window.location.hash = '#lobby';
    return;
  }

  switch (route) {
    case '#auth':
      disconnectGame();
      show(authSection);
      break;
    case '#lobby':
      disconnectGame();
      show(lobbySection);
      break;
    case '#game':
      if (!param) {
        window.location.hash = '#lobby';
        return;
      }
      show(gameSection);
      await openGame(param);
      break;
    case '#profile':
      disconnectGame();
      show(profileSection);
      await loadProfile();
      break;
    default:
      window.location.hash = signedIn ? '#lobby' : '#auth';
  }
}

function credentials(): UserCreateDto {
  return {
    username: usernameInput.value.trim(),
    password: passwordInput.value,
  };
}

document.getElementById('btn-login')?.addEventListener('click', async () => {
  try {
    await apiFetch<UserResponseDto>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials()),
    });
    await refreshSession();
    showToast('Вы вошли');
    window.location.hash = '#lobby';
  } catch (err: any) {
    showToast(err.message || 'Не удалось войти');
  }
});

document.getElementById('btn-register')?.addEventListener('click', async () => {
  try {
    const data = credentials();
    await apiFetch<UserResponseDto>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    await apiFetch<UserResponseDto>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    await refreshSession();
    showToast('Аккаунт создан');
    window.location.hash = '#lobby';
  } catch (err: any) {
    showToast(err.message || 'Не удалось зарегистрироваться');
  }
});

document.getElementById('btn-guest')?.addEventListener('click', async () => {
  try {
    await apiFetch<string>('/api/auth/anonymous', { method: 'POST' });
    await refreshSession();
    showToast('Гостевой сеанс');
    window.location.hash = '#lobby';
  } catch (err: any) {
    showToast(err.message || 'Не удалось войти как гость');
  }
});

document.getElementById('btn-logout')?.addEventListener('click', async () => {
  try {
    await apiFetch<string>('/api/auth/logout', { method: 'POST' });
  } catch {
    /* cookie всё равно нужно сбросить на клиенте через ответ сервера */
  }
  currentUser = null;
  setMe(null);
  window.location.hash = '#auth';
});

document.getElementById('btn-create-room')?.addEventListener('click', async () => {
  try {
    const room = await apiFetch<Room>('/api/rooms', { method: 'POST' });
    window.location.hash = `#game/${room.uuid}`;
  } catch (err: any) {
    showToast(err.message || 'Не удалось создать комнату');
  }
});

document.getElementById('btn-join-room')?.addEventListener('click', async () => {
  const uuid = roomUuidInput.value.trim();
  if (!uuid) {
    showToast('Введите UUID комнаты');
    return;
  }
  try {
    const room = await apiFetch<Room>(`/api/rooms/${uuid}`, { method: 'POST' });
    window.location.hash = `#game/${room.uuid || uuid}`;
  } catch (err: any) {
    window.location.hash = `#game/${uuid}`;
    showToast(err.message || 'Открываем комнату');
  }
});

document.getElementById('btn-leave-game')?.addEventListener('click', () => {
  window.location.hash = '#lobby';
});

document.getElementById('btn-copy-room')?.addEventListener('click', async () => {
  const uuid = document.getElementById('active-room-uuid')?.textContent?.trim();
  if (!uuid) return;
  try {
    await navigator.clipboard.writeText(uuid);
    showToast('UUID скопирован');
  } catch {
    showToast(uuid);
  }
});

document.getElementById('btn-profile')?.addEventListener('click', () => {
  window.location.hash = '#profile';
});

document.getElementById('btn-close-profile')?.addEventListener('click', () => {
  window.location.hash = '#lobby';
});

document.getElementById('btn-search-user')?.addEventListener('click', () => {
  const id = Number((document.getElementById('search-user-id') as HTMLInputElement).value);
  if (!Number.isFinite(id) || id <= 0) {
    showToast('Введите числовой ID');
    return;
  }
  void loadProfile(id);
});

document.getElementById('btn-my-profile')?.addEventListener('click', () => {
  void loadProfile();
});

document.getElementById('btn-load-matches')?.addEventListener('click', loadMatches);

async function loadProfile(targetId?: number) {
  const idEl = document.getElementById('profile-user-id')!;
  const nameEl = document.getElementById('profile-username')!;
  const dateEl = document.getElementById('profile-created-at')!;
  const list = document.getElementById('profile-matches-list')!;
  list.replaceChildren();
  viewedProfileId = null;
  try {
    const profile = targetId
      ? await apiFetch<UserResponseDto>(`/api/user/${targetId}`)
      : await apiFetch<UserResponseDto>('/api/user/me');
    viewedProfileId = profile.id;
    idEl.textContent = String(profile.id);
    nameEl.textContent = profile.username;
    const date = new Date(profile.createdAt);
    dateEl.textContent =
      profile.id < 0 ? 'гость' : Number.isNaN(date.getTime()) ? profile.createdAt : date.toLocaleString('ru-RU');
  } catch (err: any) {
    idEl.textContent = '—';
    nameEl.textContent = 'не найден';
    dateEl.textContent = '—';
    showToast(err.message || 'Профиль недоступен');
  }
}

async function loadMatches() {
  const list = document.getElementById('profile-matches-list')!;
  if (viewedProfileId == null) {
    showToast('Сначала откройте профиль');
    return;
  }
  if (viewedProfileId < 0) {
    list.textContent = 'У гостей нет сохранённой истории.';
    return;
  }
  list.textContent = 'Загрузка…';
  try {
    const matches = await apiFetch<MatchResponseDto[]>(`/api/player/matches/${viewedProfileId}`);
    list.replaceChildren();
    if (!matches?.length) {
      list.textContent = 'Партий пока нет.';
      return;
    }
    for (const match of matches) {
      const item = document.createElement('div');
      item.className = 'match';
      const result =
        match.result === 'WHITE_WIN'
          ? 'победа белых'
          : match.result === 'BLACK_WIN'
            ? 'победа чёрных'
            : match.result === 'DRAW'
              ? 'ничья'
              : 'не завершена';
      item.textContent = `${match.whitePlayer?.username || 'белые'} — ${match.blackPlayer?.username || 'чёрные'} · ${result}`;
      list.appendChild(item);
    }
  } catch (err: any) {
    list.textContent = 'Не удалось загрузить историю.';
    showToast(err.message);
  }
}

window.addEventListener('hashchange', () => {
  void route();
});

void (async () => {
  await refreshSession();
  await route();
})();
