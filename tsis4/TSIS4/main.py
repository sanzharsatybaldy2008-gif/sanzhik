# Главный модуль игры "Змейка"
# Pygame-приложение с пятью экранами: меню, игра, лидерборд, настройки, конец игры

import sys
import json
import pygame

import db
from game import SnakeGame
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    BLACK, WHITE, GREEN, DARK_GREEN, RED, DARK_RED,
    BLUE, YELLOW, ORANGE, PURPLE, GRAY, DARK_GRAY
)

# ─── Идентификаторы экранов ──────────────────────────────────────────────────────
STATE_MENU        = 0
STATE_GAME        = 1
STATE_LEADERBOARD = 2
STATE_SETTINGS    = 3
STATE_GAMEOVER    = 4

# ─── Путь к файлу настроек ───────────────────────────────────────────────────────
SETTINGS_PATH = "settings.json"

# ─── Цветовые пресеты для змейки ─────────────────────────────────────────────────
SNAKE_COLOR_PRESETS = [
    [0,   200, 0],    # Зелёный
    [0,   150, 255],  # Синий
    [255, 80,  80],   # Красный
    [255, 200, 0],    # Жёлтый
    [200, 0,   200],  # Фиолетовый
    [0,   220, 180],  # Бирюзовый
]


# ════════════════════════════════════════════════════════════════════════════════
# Класс кнопки
# ════════════════════════════════════════════════════════════════════════════════
class Button:
    """Универсальная кнопка интерфейса с поддержкой ховер-эффекта."""

    def __init__(self, rect: tuple, text: str,
                 color=(60, 60, 100), hover_color=(90, 90, 160),
                 text_color=WHITE, font_size=22, border_radius=8):
        self.rect         = pygame.Rect(rect)
        self.text         = text
        self.color        = color
        self.hover_color  = hover_color
        self.text_color   = text_color
        self.font_size    = font_size
        self.border_radius = border_radius
        self._font        = pygame.font.SysFont('Arial', font_size, bold=True)

    def draw(self, screen: pygame.Surface):
        """Отрисовывает кнопку (с подсветкой при наведении)."""
        mouse_pos = pygame.mouse.get_pos()
        hovered   = self.rect.collidepoint(mouse_pos)
        color     = self.hover_color if hovered else self.color

        pygame.draw.rect(screen, color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(screen, GRAY, self.rect, 1, border_radius=self.border_radius)

        surf = self._font.render(self.text, True, self.text_color)
        x    = self.rect.centerx - surf.get_width()  // 2
        y    = self.rect.centery - surf.get_height() // 2
        screen.blit(surf, (x, y))

    def is_clicked(self, pos: tuple) -> bool:
        """Возвращает True, если клик попал в область кнопки."""
        return self.rect.collidepoint(pos)


# ════════════════════════════════════════════════════════════════════════════════
# Вспомогательные функции
# ════════════════════════════════════════════════════════════════════════════════
def load_settings() -> dict:
    """Загружает настройки из settings.json. Возвращает словарь по умолчанию при ошибке."""
    try:
        with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {"snake_color": [0, 200, 0], "grid_overlay": True, "sound": False}


def save_settings(settings: dict):
    """Сохраняет настройки в settings.json."""
    try:
        with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[Настройки] Ошибка сохранения: {e}")


def draw_background(screen: pygame.Surface):
    """Рисует тёмный градиентный фон."""
    screen.fill((12, 12, 24))


def draw_title(screen: pygame.Surface, text: str, y: int, color=GREEN,
               font_size=64, bold=True):
    """Отрисовывает заголовок по центру экрана."""
    font = pygame.font.SysFont('Arial', font_size, bold=bold)
    surf = font.render(text, True, color)
    x    = WINDOW_WIDTH // 2 - surf.get_width() // 2
    screen.blit(surf, (x, y))


def draw_text(screen: pygame.Surface, text: str, x: int, y: int,
              color=WHITE, font_size=20, bold=False, center=False):
    """Отрисовывает текстовую строку."""
    font = pygame.font.SysFont('Arial', font_size, bold=bold)
    surf = font.render(text, True, color)
    if center:
        x = WINDOW_WIDTH // 2 - surf.get_width() // 2
    screen.blit(surf, (x, y))


# ════════════════════════════════════════════════════════════════════════════════
# Экран: Главное меню
# ════════════════════════════════════════════════════════════════════════════════
class MenuScreen:
    """Экран главного меню с вводом имени пользователя и навигационными кнопками."""

    BTN_W, BTN_H = 260, 48
    BTN_X        = WINDOW_WIDTH  // 2 - 130

    def __init__(self):
        self.username       = ""
        self.input_active   = True
        self.cursor_visible = True
        self._cursor_timer  = 0

        # Кнопки меню
        self.btn_play   = Button((self.BTN_X, 300, self.BTN_W, self.BTN_H),
                                 "Играть",
                                 color=(40, 120, 40), hover_color=(60, 170, 60))
        self.btn_lb     = Button((self.BTN_X, 365, self.BTN_W, self.BTN_H),
                                 "Таблица рекордов")
        self.btn_set    = Button((self.BTN_X, 430, self.BTN_W, self.BTN_H),
                                 "Настройки")
        self.btn_quit   = Button((self.BTN_X, 495, self.BTN_W, self.BTN_H),
                                 "Выход",
                                 color=(120, 40, 40), hover_color=(170, 60, 60))

        self._font_input = pygame.font.SysFont('Arial', 22)
        self._font_label = pygame.font.SysFont('Arial', 16)

    def handle_event(self, event) -> str | None:
        """
        Обрабатывает события мыши/клавиатуры.
        Возвращает строку-действие: 'play', 'leaderboard', 'settings', 'quit' или None.
        """
        if event.type == pygame.KEYDOWN:
            if self.input_active:
                if event.key == pygame.K_BACKSPACE:
                    self.username = self.username[:-1]
                elif event.key == pygame.K_RETURN:
                    if self.username.strip():
                        return 'play'
                elif event.key == pygame.K_ESCAPE:
                    self.input_active = False
                elif len(self.username) < 20:
                    char = event.unicode
                    if char.isprintable():
                        self.username += char

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            # Клик в поле ввода
            input_rect = pygame.Rect(self.BTN_X, 230, self.BTN_W, 44)
            if input_rect.collidepoint(pos):
                self.input_active = True
            else:
                self.input_active = False

            if self.btn_play.is_clicked(pos) and self.username.strip():
                return 'play'
            if self.btn_lb.is_clicked(pos):
                return 'leaderboard'
            if self.btn_set.is_clicked(pos):
                return 'settings'
            if self.btn_quit.is_clicked(pos):
                return 'quit'

        return None

    def update(self, ticks: int):
        """Обновляет мигание курсора ввода."""
        if ticks - self._cursor_timer > 500:
            self.cursor_visible = not self.cursor_visible
            self._cursor_timer  = ticks

    def draw(self, screen: pygame.Surface):
        """Отрисовывает главное меню."""
        draw_background(screen)
        draw_title(screen, "ЗМЕЙКА", 80, color=GREEN, font_size=80)
        draw_text(screen, "Введите имя игрока:",
                  self.BTN_X, 205, color=GRAY, font_size=16)

        # Поле ввода имени
        input_rect  = pygame.Rect(self.BTN_X, 230, self.BTN_W, 44)
        border_color = YELLOW if self.input_active else DARK_GRAY
        pygame.draw.rect(screen, (25, 25, 45), input_rect, border_radius=6)
        pygame.draw.rect(screen, border_color, input_rect, 2, border_radius=6)

        display_text = self.username
        if self.input_active and self.cursor_visible:
            display_text += "|"
        text_surf = self._font_input.render(display_text, True, WHITE)
        screen.blit(text_surf, (input_rect.x + 8, input_rect.y + 10))

        # Подсказка — кнопка "Играть" недоступна без имени
        if not self.username.strip():
            draw_text(screen, "Введите имя для начала",
                      self.BTN_X, 295, color=(180, 100, 100), font_size=13)

        # Кнопки
        play_alpha = 255 if self.username.strip() else 100
        self.btn_play.text_color = WHITE if self.username.strip() else GRAY
        self.btn_play.draw(screen)
        self.btn_lb.draw(screen)
        self.btn_set.draw(screen)
        self.btn_quit.draw(screen)

        # Подсказки управления
        draw_text(screen, "Стрелки / WASD — управление",
                  0, 590, color=DARK_GRAY, font_size=14, center=True)


# ════════════════════════════════════════════════════════════════════════════════
# Экран: Таблица рекордов
# ════════════════════════════════════════════════════════════════════════════════
class LeaderboardScreen:
    """Экран с топ-10 результатами из базы данных."""

    def __init__(self):
        self.records  = []
        self.btn_back = Button(
            (WINDOW_WIDTH // 2 - 100, 580, 200, 46),
            "Назад"
        )
        self._hdr_font  = pygame.font.SysFont('Arial', 18, bold=True)
        self._row_font  = pygame.font.SysFont('Arial', 17)

    def load(self):
        """Загружает данные из базы данных."""
        self.records = db.get_leaderboard()

    def handle_event(self, event) -> str | None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_back.is_clicked(event.pos):
                return 'menu'
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return 'menu'
        return None

    def draw(self, screen: pygame.Surface):
        draw_background(screen)
        draw_title(screen, "ТАБЛИЦА РЕКОРДОВ", 30, color=YELLOW, font_size=44)

        # Заголовки таблицы
        headers  = ["#", "Имя", "Счёт", "Уровень", "Дата"]
        col_x    = [40, 90, 310, 430, 530]
        line_y   = 110

        pygame.draw.line(screen, GRAY, (30, line_y + 24), (WINDOW_WIDTH - 30, line_y + 24), 1)
        for i, (h, x) in enumerate(zip(headers, col_x)):
            surf = self._hdr_font.render(h, True, ORANGE)
            screen.blit(surf, (x, line_y))

        # Строки таблицы
        if not self.records:
            draw_text(screen, "Нет записей в базе данных",
                      0, 300, color=GRAY, font_size=20, center=True)
        else:
            row_colors = [WHITE, (200, 200, 200)]
            for idx, rec in enumerate(self.records):
                row_y   = 145 + idx * 38
                r_color = YELLOW if idx == 0 else row_colors[idx % 2]

                # Подсветка первого места
                if idx == 0:
                    hl = pygame.Surface((WINDOW_WIDTH - 60, 32), pygame.SRCALPHA)
                    hl.fill((255, 220, 0, 25))
                    screen.blit(hl, (30, row_y - 2))

                # Дата
                dt_str = ""
                if rec.get('played_at'):
                    try:
                        dt_str = rec['played_at'].strftime("%d.%m.%Y %H:%M")
                    except Exception:
                        dt_str = str(rec['played_at'])[:16]

                cells = [
                    str(rec.get('rank', idx + 1)),
                    str(rec.get('username', ''))[:18],
                    str(rec.get('score', 0)),
                    str(rec.get('level_reached', 0)),
                    dt_str,
                ]
                for cell, cx in zip(cells, col_x):
                    surf = self._row_font.render(cell, True, r_color)
                    screen.blit(surf, (cx, row_y))

        self.btn_back.draw(screen)


# ════════════════════════════════════════════════════════════════════════════════
# Экран: Настройки
# ════════════════════════════════════════════════════════════════════════════════
class SettingsScreen:
    """Экран настроек: сетка, звук, цвет змейки."""

    def __init__(self, settings: dict):
        self.settings        = dict(settings)  # локальная копия
        self._selected_color = None             # индекс выбранного цвета

        # Найдём текущий индекс цвета
        for i, c in enumerate(SNAKE_COLOR_PRESETS):
            if self.settings.get('snake_color') == c:
                self._selected_color = i
                break
        if self._selected_color is None:
            self._selected_color = 0

        cx = WINDOW_WIDTH // 2

        self.btn_grid  = Button((cx - 130, 200, 260, 46),
                                self._grid_label())
        self.btn_sound = Button((cx - 130, 270, 260, 46),
                                self._sound_label())
        self.btn_save  = Button((cx - 130, 520, 260, 46),
                                "Сохранить и назад",
                                color=(40, 100, 40), hover_color=(60, 150, 60))

    def _grid_label(self) -> str:
        state = "ВКЛ" if self.settings.get('grid_overlay', True) else "ВЫКЛ"
        return f"Сетка: {state}"

    def _sound_label(self) -> str:
        state = "ВКЛ" if self.settings.get('sound', False) else "ВЫКЛ"
        return f"Звук: {state}"

    def handle_event(self, event) -> dict | str | None:
        """
        Возвращает обновлённые настройки при сохранении,
        строку 'menu' при переходе назад или None.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            # Переключение сетки
            if self.btn_grid.is_clicked(pos):
                self.settings['grid_overlay'] = not self.settings.get('grid_overlay', True)
                self.btn_grid.text = self._grid_label()

            # Переключение звука
            elif self.btn_sound.is_clicked(pos):
                self.settings['sound'] = not self.settings.get('sound', False)
                self.btn_sound.text = self._sound_label()

            # Выбор цвета змейки
            else:
                for i, (sx, sy) in enumerate(self._color_swatch_positions()):
                    rect = pygame.Rect(sx - 18, sy - 18, 36, 36)
                    if rect.collidepoint(pos):
                        self._selected_color         = i
                        self.settings['snake_color'] = SNAKE_COLOR_PRESETS[i]

            # Сохранение и выход
            if self.btn_save.is_clicked(pos):
                self.settings['snake_color'] = SNAKE_COLOR_PRESETS[self._selected_color]
                return self.settings  # возвращаем обновлённые настройки

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return 'menu'

        return None

    def _color_swatch_positions(self):
        """Возвращает координаты центров цветовых образцов."""
        cx    = WINDOW_WIDTH // 2
        total = len(SNAKE_COLOR_PRESETS)
        start = cx - (total // 2) * 52 + 26
        return [(start + i * 52, 410) for i in range(total)]

    def draw(self, screen: pygame.Surface):
        draw_background(screen)
        draw_title(screen, "НАСТРОЙКИ", 50, color=ORANGE, font_size=48)

        self.btn_grid.draw(screen)
        self.btn_sound.draw(screen)

        # Цвет змейки
        draw_text(screen, "Цвет змейки:", 0, 360, color=GRAY,
                  font_size=18, center=True)

        for i, (sx, sy) in enumerate(self._color_swatch_positions()):
            color   = SNAKE_COLOR_PRESETS[i]
            swatch  = pygame.Rect(sx - 18, sy - 18, 36, 36)
            pygame.draw.rect(screen, color, swatch, border_radius=4)
            if i == self._selected_color:
                pygame.draw.rect(screen, WHITE, swatch, 3, border_radius=4)
            else:
                pygame.draw.rect(screen, DARK_GRAY, swatch, 1, border_radius=4)

        self.btn_save.draw(screen)


# ════════════════════════════════════════════════════════════════════════════════
# Экран: Конец игры
# ════════════════════════════════════════════════════════════════════════════════
class GameOverScreen:
    """Экран с результатами сессии после окончания игры."""

    def __init__(self):
        self.score         = 0
        self.level         = 0
        self.personal_best = 0

        cx = WINDOW_WIDTH // 2
        self.btn_restart = Button((cx - 130, 430, 260, 48),
                                  "Играть снова",
                                  color=(40, 120, 40), hover_color=(60, 170, 60))
        self.btn_menu    = Button((cx - 130, 495, 260, 48),
                                  "Главное меню")

    def set_results(self, score: int, level: int, personal_best: int):
        self.score         = score
        self.level         = level
        self.personal_best = personal_best

    def handle_event(self, event) -> str | None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_restart.is_clicked(event.pos):
                return 'restart'
            if self.btn_menu.is_clicked(event.pos):
                return 'menu'
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return 'restart'
            if event.key == pygame.K_ESCAPE:
                return 'menu'
        return None

    def draw(self, screen: pygame.Surface):
        draw_background(screen)
        draw_title(screen, "ИГРА ОКОНЧЕНА", 100, color=RED, font_size=60)

        draw_text(screen, f"Финальный счёт:  {self.score}",
                  0, 230, color=YELLOW, font_size=30, bold=True, center=True)
        draw_text(screen, f"Достигнутый уровень:  {self.level}",
                  0, 280, color=(100, 200, 255), font_size=26, center=True)
        draw_text(screen, f"Личный рекорд:  {self.personal_best}",
                  0, 330, color=ORANGE, font_size=24, center=True)

        if self.score >= self.personal_best and self.score > 0:
            draw_text(screen, "Новый личный рекорд!", 0, 375,
                      color=GREEN, font_size=20, bold=True, center=True)

        self.btn_restart.draw(screen)
        self.btn_menu.draw(screen)


# ════════════════════════════════════════════════════════════════════════════════
# Основное приложение
# ════════════════════════════════════════════════════════════════════════════════
class App:
    """Главный класс приложения — управляет состояниями и главным циклом."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Змейка")

        self.clock = pygame.time.Clock()
        self.font  = pygame.font.SysFont('Arial', 18)

        # Загрузка настроек
        self.settings = load_settings()

        # Инициализация таблиц БД
        db.create_tables()

        # Текущее состояние
        self.state    = STATE_MENU
        self.game     = None
        self.username = ""
        self.player_id = -1
        self.personal_best = 0

        # Флаг: была ли сессия уже сохранена
        self._session_saved = False

        # Создание экранов
        self.menu_screen      = MenuScreen()
        self.lb_screen        = LeaderboardScreen()
        self.settings_screen  = SettingsScreen(self.settings)
        self.gameover_screen  = GameOverScreen()

    # ────────────────────────────────────────────────────────────────────────────
    def _start_game(self):
        """Инициализирует новую игру для текущего игрока."""
        self.username      = self.menu_screen.username.strip()
        self.player_id     = db.get_or_create_player(self.username)
        self.personal_best = db.get_personal_best(self.player_id)
        self.game          = SnakeGame(
            username=self.username,
            player_id=self.player_id,
            personal_best=self.personal_best,
            settings=self.settings,
        )
        self._session_saved = False
        self.state          = STATE_GAME

    def _restart_game(self):
        """Перезапускает игру с тем же игроком."""
        self.personal_best = db.get_personal_best(self.player_id)
        self.game          = SnakeGame(
            username=self.username,
            player_id=self.player_id,
            personal_best=self.personal_best,
            settings=self.settings,
        )
        self._session_saved = False
        self.state          = STATE_GAME

    def _save_session_if_needed(self):
        """Сохраняет результат сессии в БД (только один раз)."""
        if not self._session_saved and self.game:
            db.save_session(self.player_id, self.game.score, self.game.level)
            self._session_saved = True

    # ────────────────────────────────────────────────────────────────────────────
    def run(self):
        """Главный цикл приложения."""
        running = True
        while running:
            ticks = pygame.time.get_ticks()

            # ── Обработка событий ─────────────────────────────────────────────
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.state == STATE_GAME and self.game and self.game.game_over_flag:
                        self._save_session_if_needed()
                    running = False
                    break

                # ── Меню ──────────────────────────────────────────────────────
                if self.state == STATE_MENU:
                    action = self.menu_screen.handle_event(event)
                    if action == 'play':
                        self._start_game()
                    elif action == 'leaderboard':
                        self.lb_screen.load()
                        self.state = STATE_LEADERBOARD
                    elif action == 'settings':
                        self.settings_screen = SettingsScreen(self.settings)
                        self.state = STATE_SETTINGS
                    elif action == 'quit':
                        running = False

                # ── Игра ──────────────────────────────────────────────────────
                elif self.state == STATE_GAME:
                    if event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_UP, pygame.K_w):
                            self.game.change_direction((0, -1))
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            self.game.change_direction((0, 1))
                        elif event.key in (pygame.K_LEFT, pygame.K_a):
                            self.game.change_direction((-1, 0))
                        elif event.key in (pygame.K_RIGHT, pygame.K_d):
                            self.game.change_direction((1, 0))
                        elif event.key == pygame.K_ESCAPE:
                            # Выход в меню без сохранения
                            self.state = STATE_MENU

                # ── Лидерборд ─────────────────────────────────────────────────
                elif self.state == STATE_LEADERBOARD:
                    action = self.lb_screen.handle_event(event)
                    if action == 'menu':
                        self.state = STATE_MENU

                # ── Настройки ─────────────────────────────────────────────────
                elif self.state == STATE_SETTINGS:
                    result = self.settings_screen.handle_event(event)
                    if isinstance(result, dict):
                        self.settings = result
                        save_settings(self.settings)
                        self.state = STATE_MENU
                    elif result == 'menu':
                        self.state = STATE_MENU

                # ── Конец игры ────────────────────────────────────────────────
                elif self.state == STATE_GAMEOVER:
                    action = self.gameover_screen.handle_event(event)
                    if action == 'restart':
                        self._restart_game()
                    elif action == 'menu':
                        self.state = STATE_MENU

            if not running:
                break

            # ── Обновление логики ─────────────────────────────────────────────
            if self.state == STATE_MENU:
                self.menu_screen.update(ticks)

            elif self.state == STATE_GAME and self.game:
                self.game.update(ticks)

                # Переход к экрану конца игры
                if self.game.game_over_flag:
                    self._save_session_if_needed()
                    pb = db.get_personal_best(self.player_id)
                    self.gameover_screen.set_results(
                        self.game.score,
                        self.game.level,
                        pb
                    )
                    self.state = STATE_GAMEOVER

            # ── Отрисовка ─────────────────────────────────────────────────────
            if self.state == STATE_MENU:
                self.menu_screen.draw(self.screen)

            elif self.state == STATE_GAME and self.game:
                self.game.draw(self.screen, self.font, self.settings)

            elif self.state == STATE_LEADERBOARD:
                self.lb_screen.draw(self.screen)

            elif self.state == STATE_SETTINGS:
                self.settings_screen.draw(self.screen)

            elif self.state == STATE_GAMEOVER:
                self.gameover_screen.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)  # Основной цикл — 60 FPS (движение регулируется таймером)

        pygame.quit()
        sys.exit()


# ─── Точка входа ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.run()
