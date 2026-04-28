# Модуль игровой логики "Змейка"
# Содержит класс SnakeGame со всей механикой игры

import pygame
import random
from config import (
    GRID_SIZE, COLS, ROWS, WINDOW_HEIGHT, WINDOW_WIDTH,
    FPS_BASE, FOOD_WEIGHTS, POWERUP_TYPES, LEVEL_THRESHOLD,
    BLACK, WHITE, GREEN, DARK_GREEN, RED, DARK_RED,
    BLUE, YELLOW, ORANGE, PURPLE, GRAY, DARK_GRAY
)

# ─── Направления движения ────────────────────────────────────────────────────────
UP    = (0, -1)
DOWN  = (0,  1)
LEFT  = (-1, 0)
RIGHT = (1,  0)

# ─── Цвета еды по типу ───────────────────────────────────────────────────────────
FOOD_COLORS = {
    'normal': (255, 80,  80),   # Красный — обычная еда
    'bonus':  (255, 200, 0),    # Жёлтый  — бонусная еда
    'super':  (180, 0,   220),  # Фиолетовый — супер-еда
}

# ─── Время жизни еды (в миллисекундах) ──────────────────────────────────────────
FOOD_LIFETIMES = {
    'normal': 10_000,  # 10 секунд
    'bonus':   7_000,  # 7 секунд
    'super':   5_000,  # 5 секунд
}

# ─── Цвета бонусов ───────────────────────────────────────────────────────────────
POWERUP_COLORS = {
    'speed':  (0,   200, 255),  # Голубой — ускорение
    'slow':   (100, 255, 100),  # Светло-зелёный — замедление
    'shield': (255, 200, 50),   # Золотой — щит
}

POWERUP_LABELS = {
    'speed':  'УСКОРЕНИЕ',
    'slow':   'ЗАМЕДЛЕНИЕ',
    'shield': 'ЩИТ',
}

# ─── Время жизни бонуса на поле и длительность эффекта ──────────────────────────
POWERUP_FIELD_LIFETIME = 8_000    # 8 секунд на поле
POWERUP_EFFECT_DURATION = 5_000   # 5 секунд действия эффекта

# ─── Время жизни ядовитой еды ────────────────────────────────────────────────────
POISON_LIFETIME = 8_000  # 8 секунд

# ─── Максимальное количество единиц еды на поле ─────────────────────────────────
MAX_FOODS = 3


class SnakeGame:
    """Основной класс игровой логики — управляет состоянием игры "Змейка"."""

    def __init__(self, username: str, player_id: int, personal_best: int, settings: dict):
        self.username      = username
        self.player_id     = player_id
        self.personal_best = personal_best
        self.settings      = settings

        # Инициализация состояния
        self.reset()

    # ────────────────────────────────────────────────────────────────────────────
    def reset(self):
        """Сбрасывает игру в начальное состояние."""
        # Змейка стартует в центре поля, длина 3 клетки, движется вправо
        cx, cy = COLS // 2, ROWS // 2
        self.snake = [[cx - i, cy] for i in range(3)]
        self.direction      = RIGHT
        self.next_direction = RIGHT

        self.score          = 0
        self.level          = 1
        self._foods_eaten   = 0  # счётчик для перехода уровня

        self.foods         = []   # список активных единиц еды
        self.poison_food   = None # ядовитая еда
        self.powerup       = None # бонус на поле
        self.active_powerup = None # текущий активный бонус
        self.obstacles     = []   # препятствия

        self.speed         = FPS_BASE
        self.game_over_flag = False
        self.shield_active  = False

        self._last_move_time = 0  # время последнего шага змейки

        # Генерируем начальную еду
        for _ in range(MAX_FOODS):
            self.place_food()

    # ────────────────────────────────────────────────────────────────────────────
    def _occupied(self) -> set:
        """Возвращает множество занятых позиций на поле."""
        occupied = set(map(tuple, self.snake))
        occupied.update(map(tuple, self.obstacles))
        for f in self.foods:
            occupied.add(tuple(f['pos']))
        if self.poison_food:
            occupied.add(tuple(self.poison_food['pos']))
        if self.powerup:
            occupied.add(tuple(self.powerup['pos']))
        return occupied

    def _random_free_pos(self) -> list:
        """Возвращает случайную свободную позицию на поле."""
        occupied = self._occupied()
        free = [
            [c, r]
            for c in range(COLS)
            for r in range(ROWS)
            if (c, r) not in occupied
        ]
        if not free:
            return [0, 0]
        return random.choice(free)

    # ────────────────────────────────────────────────────────────────────────────
    def place_food(self):
        """Размещает одну единицу еды на поле, если их меньше MAX_FOODS."""
        if len(self.foods) >= MAX_FOODS:
            return
        pos       = self._random_free_pos()
        food_type = random.choices(
            list(FOOD_WEIGHTS.keys()),
            weights=list(FOOD_WEIGHTS.values())
        )[0]
        self.foods.append({
            'pos':        pos,
            'type':       food_type,
            'points':     FOOD_WEIGHTS[food_type],
            'spawn_time': pygame.time.get_ticks(),
            'lifetime':   FOOD_LIFETIMES[food_type],
        })

    def place_poison(self):
        """Размещает ядовитую еду на поле."""
        if self.poison_food is not None:
            return
        pos = self._random_free_pos()
        self.poison_food = {
            'pos':        pos,
            'spawn_time': pygame.time.get_ticks(),
            'lifetime':   POISON_LIFETIME,
        }

    def place_powerup(self):
        """Размещает бонус на поле."""
        if self.powerup is not None:
            return
        pos    = self._random_free_pos()
        p_type = random.choice(POWERUP_TYPES)
        self.powerup = {
            'pos':        pos,
            'type':       p_type,
            'spawn_time': pygame.time.get_ticks(),
            'field_lifetime': POWERUP_FIELD_LIFETIME,
        }

    def place_obstacles(self, level: int):
        """
        Генерирует препятствия для текущего уровня (начиная с уровня 3).
        Количество: 5 + level*2. Центральная зона 5×5 вокруг старта исключена.
        """
        count    = 5 + level * 2
        cx, cy   = COLS // 2, ROWS // 2
        safe_set = {
            (cx + dx, cy + dy)
            for dx in range(-2, 3)
            for dy in range(-2, 3)
        }
        occupied = set(map(tuple, self.snake)) | safe_set
        candidates = [
            [c, r]
            for c in range(COLS)
            for r in range(ROWS)
            if (c, r) not in occupied
        ]
        random.shuffle(candidates)
        self.obstacles = candidates[:count]

    # ────────────────────────────────────────────────────────────────────────────
    def change_direction(self, new_dir: tuple):
        """Меняет направление движения змейки (нельзя развернуться на 180°)."""
        opposite = (-new_dir[0], -new_dir[1])
        if new_dir != opposite or len(self.snake) == 1:
            if new_dir != (-self.direction[0], -self.direction[1]):
                self.next_direction = new_dir

    # ────────────────────────────────────────────────────────────────────────────
    def get_speed(self) -> float:
        """Возвращает текущую скорость с учётом активного бонуса."""
        base = FPS_BASE + (self.level - 1) * 0.5  # небольшое ускорение с уровнем
        if self.active_powerup:
            t = self.active_powerup['type']
            if t == 'speed':
                return base * 1.5
            elif t == 'slow':
                return base * 0.6
        return base

    # ────────────────────────────────────────────────────────────────────────────
    def eat_food(self, food: dict):
        """Начисляет очки за съеденную еду и проверяет переход на новый уровень."""
        self.score        += food['points']
        self._foods_eaten += 1

        # Обновляем личный рекорд в рамках текущей сессии
        if self.score > self.personal_best:
            self.personal_best = self.score

        # Переход на следующий уровень
        if self._foods_eaten >= LEVEL_THRESHOLD:
            self._foods_eaten = 0
            self.level       += 1
            # Генерируем препятствия начиная с 3-го уровня
            if self.level >= 3:
                self.place_obstacles(self.level)

    # ────────────────────────────────────────────────────────────────────────────
    def check_collision(self) -> bool:
        """
        Проверяет столкновения головы змейки.
        Возвращает True, если игра должна завершиться.
        """
        head = self.snake[0]

        # Выход за границы поля
        if not (0 <= head[0] < COLS and 0 <= head[1] < ROWS):
            if self.shield_active:
                self.shield_active = False
                self.active_powerup = None
                # Возвращаем голову в допустимую зону
                head[0] = max(0, min(COLS - 1, head[0]))
                head[1] = max(0, min(ROWS - 1, head[1]))
                return False
            return True

        # Столкновение с телом змейки
        if head in self.snake[1:]:
            if self.shield_active:
                self.shield_active = False
                self.active_powerup = None
                return False
            return True

        # Столкновение с препятствием
        if head in self.obstacles:
            if self.shield_active:
                self.shield_active = False
                self.active_powerup = None
                return False
            return True

        return False

    # ────────────────────────────────────────────────────────────────────────────
    def update(self, current_ticks: int):
        """
        Основной метод обновления игрового состояния.
        Вызывается каждый кадр; движение происходит только при истечении таймера.
        """
        if self.game_over_flag:
            return

        # ── Проверяем, пора ли делать шаг ───────────────────────────────────────
        interval = int(1000 / max(1, self.get_speed()))
        if current_ticks - self._last_move_time < interval:
            return
        self._last_move_time = current_ticks

        # ── Применяем запланированное направление ────────────────────────────────
        self.direction = self.next_direction

        # ── Перемещаем голову ────────────────────────────────────────────────────
        new_head = [
            self.snake[0][0] + self.direction[0],
            self.snake[0][1] + self.direction[1],
        ]
        self.snake.insert(0, new_head)

        # ── Проверка съедания обычной еды ────────────────────────────────────────
        eaten_food = None
        for food in self.foods:
            if new_head == food['pos']:
                eaten_food = food
                break

        if eaten_food:
            self.foods.remove(eaten_food)
            self.eat_food(eaten_food)
            self.place_food()
            # Хвост не удаляем — змейка растёт
        else:
            self.snake.pop()  # Убираем хвост — обычное движение

        # ── Проверка столкновений ────────────────────────────────────────────────
        if self.check_collision():
            self.game_over_flag = True
            return

        # ── Проверка ядовитой еды ────────────────────────────────────────────────
        if self.poison_food and new_head == self.poison_food['pos']:
            self.poison_food = None
            # Сначала укорачиваем, потом проверяем длину (по заданию: если <=1 — game over)
            self.snake = self.snake[:-min(2, len(self.snake) - 1)]
            if len(self.snake) <= 1:
                self.game_over_flag = True
                return

        # ── Проверка бонуса ──────────────────────────────────────────────────────
        if self.powerup and new_head == self.powerup['pos']:
            p_type = self.powerup['type']
            self.powerup = None
            self.active_powerup = {
                'type':       p_type,
                'start_time': current_ticks,
                'duration':   POWERUP_EFFECT_DURATION,
            }
            if p_type == 'shield':
                self.shield_active = True

        # ── Истечение срока бонуса ───────────────────────────────────────────────
        if self.active_powerup:
            elapsed = current_ticks - self.active_powerup['start_time']
            if elapsed >= self.active_powerup['duration']:
                if self.active_powerup['type'] == 'shield':
                    self.shield_active = False
                self.active_powerup = None

        # ── Истечение срока еды ──────────────────────────────────────────────────
        expired = [
            f for f in self.foods
            if current_ticks - f['spawn_time'] >= f['lifetime']
        ]
        for f in expired:
            self.foods.remove(f)
            self.place_food()

        # ── Истечение срока ядовитой еды ─────────────────────────────────────────
        if self.poison_food:
            if current_ticks - self.poison_food['spawn_time'] >= self.poison_food['lifetime']:
                self.poison_food = None

        # ── Истечение срока бонуса на поле ───────────────────────────────────────
        if self.powerup:
            if current_ticks - self.powerup['spawn_time'] >= self.powerup['field_lifetime']:
                self.powerup = None

        # ── Случайное появление ядовитой еды и бонусов ───────────────────────────
        # Вероятность привязана к шагу змейки (~15% яд, ~10% бонус за шаг)
        if self.poison_food is None and random.random() < 0.15:
            self.place_poison()
        if self.powerup is None and self.active_powerup is None and random.random() < 0.10:
            self.place_powerup()

    # ────────────────────────────────────────────────────────────────────────────
    def draw(self, screen: pygame.Surface, font: pygame.font.Font, settings: dict):
        """
        Отрисовывает всё игровое поле:
        - фон и сетку
        - препятствия, еду, ядовитую еду, бонус, змейку
        - HUD (очки, уровень, рекорд)
        - индикатор активного бонуса
        """
        HUD_HEIGHT = 50
        field_rect = pygame.Rect(0, HUD_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT - HUD_HEIGHT)

        # ── Фон поля ─────────────────────────────────────────────────────────────
        pygame.draw.rect(screen, (15, 15, 30), field_rect)

        # ── Сетка ────────────────────────────────────────────────────────────────
        if settings.get('grid_overlay', True):
            grid_color = (30, 30, 50)
            for c in range(COLS + 1):
                x = c * GRID_SIZE
                pygame.draw.line(screen, grid_color,
                                 (x, HUD_HEIGHT), (x, WINDOW_HEIGHT))
            for r in range(ROWS + 1):
                y = HUD_HEIGHT + r * GRID_SIZE
                pygame.draw.line(screen, grid_color, (0, y), (WINDOW_WIDTH, y))

        # ── Препятствия ───────────────────────────────────────────────────────────
        for obs in self.obstacles:
            rect = pygame.Rect(obs[0] * GRID_SIZE, HUD_HEIGHT + obs[1] * GRID_SIZE,
                               GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, DARK_GRAY, rect)
            pygame.draw.rect(screen, GRAY, rect, 1)

        # ── Еда ───────────────────────────────────────────────────────────────────
        for food in self.foods:
            fx, fy = food['pos']
            color  = FOOD_COLORS[food['type']]
            center = (
                fx * GRID_SIZE + GRID_SIZE // 2,
                HUD_HEIGHT + fy * GRID_SIZE + GRID_SIZE // 2
            )
            # Мигание при приближении к истечению
            now      = pygame.time.get_ticks()
            elapsed  = now - food['spawn_time']
            remain   = food['lifetime'] - elapsed
            if remain < 2000 and (now // 300) % 2 == 0:
                color = WHITE
            pygame.draw.circle(screen, color, center, GRID_SIZE // 2 - 2)
            # Очки — маленький текст рядом с едой
            pts_surf = font.render(f"+{food['points']}", True, WHITE)
            screen.blit(pts_surf, (center[0] + 6, center[1] - 14))

        # ── Ядовитая еда ─────────────────────────────────────────────────────────
        if self.poison_food:
            px, py  = self.poison_food['pos']
            p_center = (
                px * GRID_SIZE + GRID_SIZE // 2,
                HUD_HEIGHT + py * GRID_SIZE + GRID_SIZE // 2
            )
            now    = pygame.time.get_ticks()
            elapsed = now - self.poison_food['spawn_time']
            remain  = self.poison_food['lifetime'] - elapsed
            p_color = (0, 220, 80) if (remain >= 2000 or (now // 300) % 2 == 0) else WHITE
            pygame.draw.circle(screen, p_color, p_center, GRID_SIZE // 2 - 2)
            pygame.draw.circle(screen, BLACK, p_center, GRID_SIZE // 2 - 5)
            cross_color = (0, 220, 80)
            cx, cy_ = p_center
            pygame.draw.line(screen, cross_color,
                             (cx - 4, cy_), (cx + 4, cy_), 2)
            pygame.draw.line(screen, cross_color,
                             (cx, cy_ - 4), (cx, cy_ + 4), 2)

        # ── Бонус на поле ─────────────────────────────────────────────────────────
        if self.powerup:
            bx, by  = self.powerup['pos']
            b_center = (
                bx * GRID_SIZE + GRID_SIZE // 2,
                HUD_HEIGHT + by * GRID_SIZE + GRID_SIZE // 2
            )
            b_color = POWERUP_COLORS[self.powerup['type']]
            pygame.draw.polygon(screen, b_color, [
                (b_center[0], b_center[1] - GRID_SIZE // 2 + 2),
                (b_center[0] + GRID_SIZE // 2 - 2, b_center[1] + GRID_SIZE // 2 - 2),
                (b_center[0] - GRID_SIZE // 2 + 2, b_center[1] + GRID_SIZE // 2 - 2),
            ])

        # ── Змейка ────────────────────────────────────────────────────────────────
        snake_color = tuple(settings.get('snake_color', list(GREEN)))
        for idx, seg in enumerate(self.snake):
            rect = pygame.Rect(
                seg[0] * GRID_SIZE + 1,
                HUD_HEIGHT + seg[1] * GRID_SIZE + 1,
                GRID_SIZE - 2,
                GRID_SIZE - 2
            )
            # Голова ярче
            if idx == 0:
                color = WHITE if self.shield_active else snake_color
            else:
                # Плавное затемнение хвоста
                factor = max(0.4, 1 - idx / max(len(self.snake), 1) * 0.6)
                color  = tuple(int(c * factor) for c in snake_color)
            pygame.draw.rect(screen, color, rect, border_radius=3)

        # ── HUD (верхняя панель) ──────────────────────────────────────────────────
        pygame.draw.rect(screen, (20, 20, 40), pygame.Rect(0, 0, WINDOW_WIDTH, HUD_HEIGHT))
        pygame.draw.line(screen, GRAY, (0, HUD_HEIGHT), (WINDOW_WIDTH, HUD_HEIGHT), 1)

        hud_font = pygame.font.SysFont('Arial', 18, bold=True)

        score_text = hud_font.render(f"Очки: {self.score}", True, YELLOW)
        level_text = hud_font.render(f"Уровень: {self.level}", True, (100, 200, 255))
        best_text  = hud_font.render(f"Рекорд: {self.personal_best}", True, ORANGE)

        screen.blit(score_text, (10, 14))
        screen.blit(level_text, (WINDOW_WIDTH // 2 - level_text.get_width() // 2, 14))
        screen.blit(best_text,  (WINDOW_WIDTH - best_text.get_width() - 10, 14))

        # ── Индикатор активного бонуса ────────────────────────────────────────────
        if self.active_powerup:
            now      = pygame.time.get_ticks()
            elapsed  = now - self.active_powerup['start_time']
            remain_s = max(0, (self.active_powerup['duration'] - elapsed) / 1000)
            label    = POWERUP_LABELS.get(self.active_powerup['type'], '')
            p_color  = POWERUP_COLORS.get(self.active_powerup['type'], WHITE)
            pu_text  = hud_font.render(
                f"{label}: {remain_s:.1f}с", True, p_color
            )
            # Рисуем в HUD-панели рядом с очками (y=14), справа от уровня
            screen.blit(pu_text, (WINDOW_WIDTH // 2 - pu_text.get_width() // 2, 30))
