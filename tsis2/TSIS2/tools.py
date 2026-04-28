"""
Модуль инструментов для рисования.
Содержит классы всех инструментов: карандаш, линия, прямоугольник,
круг, квадрат, прямоугольный треугольник, равносторонний треугольник,
ромб, ластик, заливка и текст.
"""

import pygame
import math
from collections import deque


class BaseTool:
    """Базовый класс инструмента рисования."""

    def __init__(self):
        self.color = (0, 0, 0)          # текущий цвет
        self.size = 2                    # толщина линии
        self.start_pos = None           # начальная позиция нажатия
        self.drawing = False            # флаг активного рисования

    def on_mouse_down(self, pos, canvas):
        """Обработка нажатия кнопки мыши."""
        self.start_pos = pos
        self.drawing = True

    def on_mouse_move(self, pos, canvas, screen_canvas):
        """Обработка движения мыши."""
        pass

    def on_mouse_up(self, pos, canvas):
        """Обработка отпускания кнопки мыши."""
        self.drawing = False
        self.start_pos = None

    def draw_preview(self, surface, pos):
        """Отрисовка предварительного просмотра фигуры."""
        pass


class PencilTool(BaseTool):
    """Инструмент «Карандаш» — рисует линию вдоль траектории мыши."""

    def __init__(self):
        super().__init__()
        self.prev_pos = None  # предыдущая позиция для рисования непрерывной линии

    def on_mouse_down(self, pos, canvas):
        super().on_mouse_down(pos, canvas)
        self.prev_pos = pos
        # Рисуем точку при нажатии
        pygame.draw.circle(canvas, self.color, pos, max(1, self.size // 2))

    def on_mouse_move(self, pos, canvas, screen_canvas):
        """Рисует линию от предыдущей позиции до текущей."""
        if self.drawing and self.prev_pos:
            pygame.draw.line(canvas, self.color, self.prev_pos, pos, self.size)
            # Рисуем кружочки на концах для сглаживания
            pygame.draw.circle(canvas, self.color, pos, max(1, self.size // 2))
        self.prev_pos = pos

    def on_mouse_up(self, pos, canvas):
        super().on_mouse_up(pos, canvas)
        self.prev_pos = None


class LineTool(BaseTool):
    """Инструмент «Линия» — рисует прямую линию от начальной до конечной точки."""

    def on_mouse_down(self, pos, canvas):
        super().on_mouse_down(pos, canvas)

    def draw_preview(self, surface, pos):
        """Рисует предварительный просмотр линии на переданной поверхности."""
        if self.drawing and self.start_pos:
            pygame.draw.line(surface, self.color, self.start_pos, pos, self.size)

    def on_mouse_up(self, pos, canvas):
        """Финализирует линию на холсте."""
        if self.drawing and self.start_pos:
            pygame.draw.line(canvas, self.color, self.start_pos, pos, self.size)
        super().on_mouse_up(pos, canvas)


class RectTool(BaseTool):
    """Инструмент «Прямоугольник» — рисует прямоугольник."""

    def _get_rect(self, pos):
        """Вычисляет pygame.Rect из начальной и текущей позиций."""
        x = min(self.start_pos[0], pos[0])
        y = min(self.start_pos[1], pos[1])
        w = abs(pos[0] - self.start_pos[0])
        h = abs(pos[1] - self.start_pos[1])
        return pygame.Rect(x, y, w, h)

    def draw_preview(self, surface, pos):
        if self.drawing and self.start_pos:
            rect = self._get_rect(pos)
            if rect.width > 0 and rect.height > 0:
                pygame.draw.rect(surface, self.color, rect, self.size)

    def on_mouse_up(self, pos, canvas):
        if self.drawing and self.start_pos:
            rect = self._get_rect(pos)
            if rect.width > 0 and rect.height > 0:
                pygame.draw.rect(canvas, self.color, rect, self.size)
        super().on_mouse_up(pos, canvas)


class CircleTool(BaseTool):
    """Инструмент «Круг» — рисует окружность, радиус задаётся расстоянием."""

    def _get_center_radius(self, pos):
        """Вычисляет центр и радиус окружности."""
        center = self.start_pos
        radius = int(math.hypot(pos[0] - center[0], pos[1] - center[1]))
        return center, radius

    def draw_preview(self, surface, pos):
        if self.drawing and self.start_pos:
            center, radius = self._get_center_radius(pos)
            if radius > 0:
                pygame.draw.circle(surface, self.color, center, radius, self.size)

    def on_mouse_up(self, pos, canvas):
        if self.drawing and self.start_pos:
            center, radius = self._get_center_radius(pos)
            if radius > 0:
                pygame.draw.circle(canvas, self.color, center, radius, self.size)
        super().on_mouse_up(pos, canvas)


class SquareTool(BaseTool):
    """Инструмент «Квадрат» — как прямоугольник, но с принудительно равными сторонами."""

    def _get_rect(self, pos):
        """Вычисляет квадратный Rect из начальной и текущей позиций."""
        dx = pos[0] - self.start_pos[0]
        dy = pos[1] - self.start_pos[1]
        # Берём меньшую из сторон, сохраняем знаки для направления
        side = min(abs(dx), abs(dy))
        sx = self.start_pos[0]
        sy = self.start_pos[1]
        ex = sx + (side if dx >= 0 else -side)
        ey = sy + (side if dy >= 0 else -side)
        x = min(sx, ex)
        y = min(sy, ey)
        return pygame.Rect(x, y, side, side)

    def draw_preview(self, surface, pos):
        if self.drawing and self.start_pos:
            rect = self._get_rect(pos)
            if rect.width > 0:
                pygame.draw.rect(surface, self.color, rect, self.size)

    def on_mouse_up(self, pos, canvas):
        if self.drawing and self.start_pos:
            rect = self._get_rect(pos)
            if rect.width > 0:
                pygame.draw.rect(canvas, self.color, rect, self.size)
        super().on_mouse_up(pos, canvas)


class RightTriangleTool(BaseTool):
    """
    Инструмент «Прямоугольный треугольник».
    Вершины: start_pos (прямой угол), (pos.x, start_pos.y), (start_pos.x, pos.y)
    """

    def _get_points(self, pos):
        """Вычисляет три вершины прямоугольного треугольника."""
        x0, y0 = self.start_pos
        x1, y1 = pos
        # Прямой угол в start_pos
        return [(x0, y0), (x1, y0), (x0, y1)]

    def draw_preview(self, surface, pos):
        if self.drawing and self.start_pos:
            pts = self._get_points(pos)
            pygame.draw.polygon(surface, self.color, pts, self.size)

    def on_mouse_up(self, pos, canvas):
        if self.drawing and self.start_pos:
            pts = self._get_points(pos)
            pygame.draw.polygon(canvas, self.color, pts, self.size)
        super().on_mouse_up(pos, canvas)


class EqTriangleTool(BaseTool):
    """
    Инструмент «Равносторонний треугольник».
    start_pos — вершина, pos определяет основание (длина стороны = расстояние).
    """

    def _get_points(self, pos):
        """Вычисляет три вершины равностороннего треугольника."""
        x0, y0 = self.start_pos
        x1, y1 = pos
        # Вычисляем длину стороны
        side = math.hypot(x1 - x0, y1 - y0)
        if side < 1:
            return None
        # Угол основания
        angle = math.atan2(y1 - y0, x1 - x0)
        # Третья вершина — поворот на 60° от линии start->pos
        angle2 = angle - math.pi / 3
        x2 = x0 + side * math.cos(angle2)
        y2 = y0 + side * math.sin(angle2)
        return [(x0, y0), (x1, y1), (int(x2), int(y2))]

    def draw_preview(self, surface, pos):
        if self.drawing and self.start_pos:
            pts = self._get_points(pos)
            if pts:
                pygame.draw.polygon(surface, self.color, pts, self.size)

    def on_mouse_up(self, pos, canvas):
        if self.drawing and self.start_pos:
            pts = self._get_points(pos)
            if pts:
                pygame.draw.polygon(canvas, self.color, pts, self.size)
        super().on_mouse_up(pos, canvas)


class RhombusTool(BaseTool):
    """
    Инструмент «Ромб».
    start_pos — центр ромба, pos задаёт размер (полудиагонали).
    """

    def _get_points(self, pos):
        """Вычисляет четыре вершины ромба по центру и одному углу."""
        cx, cy = self.start_pos
        dx = abs(pos[0] - cx)
        dy = abs(pos[1] - cy)
        if dx < 1:
            dx = 1
        if dy < 1:
            dy = 1
        # Четыре вершины: верх, право, низ, лево
        return [
            (cx, cy - dy),  # верх
            (cx + dx, cy),  # право
            (cx, cy + dy),  # низ
            (cx - dx, cy),  # лево
        ]

    def draw_preview(self, surface, pos):
        if self.drawing and self.start_pos:
            pts = self._get_points(pos)
            pygame.draw.polygon(surface, self.color, pts, self.size)

    def on_mouse_up(self, pos, canvas):
        if self.drawing and self.start_pos:
            pts = self._get_points(pos)
            pygame.draw.polygon(canvas, self.color, pts, self.size)
        super().on_mouse_up(pos, canvas)


class EraserTool(BaseTool):
    """Инструмент «Ластик» — рисует линию цветом фона (белый)."""

    def __init__(self):
        super().__init__()
        self.bg_color = (255, 255, 255)  # цвет фона холста
        self.prev_pos = None

    def on_mouse_down(self, pos, canvas):
        super().on_mouse_down(pos, canvas)
        self.prev_pos = pos
        pygame.draw.circle(canvas, self.bg_color, pos, max(2, self.size))

    def on_mouse_move(self, pos, canvas, screen_canvas):
        """Стирает, рисуя линию цвета фона."""
        if self.drawing and self.prev_pos:
            pygame.draw.line(canvas, self.bg_color, self.prev_pos, pos, self.size * 2)
            pygame.draw.circle(canvas, self.bg_color, pos, max(2, self.size))
        self.prev_pos = pos

    def on_mouse_up(self, pos, canvas):
        super().on_mouse_up(pos, canvas)
        self.prev_pos = None


class TextTool(BaseTool):
    """
    Инструмент «Текст».
    По клику устанавливает позицию ввода, по нажатию клавиш накапливает строку,
    по Enter или Escape завершает ввод и отрисовывает текст на холсте.
    """

    def __init__(self):
        super().__init__()
        self.active = False          # флаг активного ввода
        self.text = ""               # накопленный текст
        self.position = (0, 0)       # позиция на холсте
        self.font_size = 20          # размер шрифта в пикселях

    def on_mouse_down(self, pos, canvas):
        """Начинает ввод текста в указанной позиции."""
        self.position = pos
        self.active = True
        self.text = ""
        self.drawing = True

    def on_key_down(self, event, canvas, font):
        """
        Обрабатывает нажатие клавиши при активном вводе.
        Backspace — удаляет последний символ.
        Enter — финализирует текст на холсте.
        Escape — отменяет ввод.
        Остальные — добавляют символ к строке.
        """
        if not self.active:
            return False  # ввод не активен

        if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
            # Финализируем текст на холсте
            self._render_to_canvas(canvas, font)
            self.active = False
            self.text = ""
            self.drawing = False
            return True
        elif event.key == pygame.K_ESCAPE:
            # Отменяем ввод без отрисовки
            self.active = False
            self.text = ""
            self.drawing = False
            return True
        elif event.key == pygame.K_BACKSPACE:
            # Удаляем последний символ
            self.text = self.text[:-1]
            return True
        else:
            # Добавляем символ (unicode для поддержки кириллицы)
            if event.unicode:
                self.text += event.unicode
            return True

    def _render_to_canvas(self, canvas, font):
        """Отрисовывает накопленный текст на холсте."""
        if self.text:
            surf = font.render(self.text, True, self.color)
            canvas.blit(surf, self.position)

    def draw_cursor_preview(self, surface, font):
        """
        Рисует предварительный просмотр текста с курсором.
        Вызывается каждый кадр при активном вводе.
        """
        if self.active:
            # Рисуем текст с мигающим курсором
            preview = self.text + "|"
            surf = font.render(preview, True, self.color)
            surface.blit(surf, self.position)

    def on_mouse_up(self, pos, canvas):
        """При текстовом инструменте mouse_up не завершает ввод."""
        pass  # ввод завершается только по Enter/Escape


class FloodFillTool(BaseTool):
    """
    Инструмент «Заливка» (BFS flood fill).
    Заполняет область одного цвета новым цветом начиная с позиции клика.
    """

    def __init__(self):
        super().__init__()
        self.tolerance = 0  # допуск совпадения цвета (0 = точное совпадение)

    def _colors_match(self, c1, c2):
        """Проверяет совпадение двух цветов с учётом допуска."""
        return (abs(int(c1[0]) - int(c2[0])) <= self.tolerance and
                abs(int(c1[1]) - int(c2[1])) <= self.tolerance and
                abs(int(c1[2]) - int(c2[2])) <= self.tolerance)

    def flood_fill(self, surface, pos, fill_color):
        """
        BFS-заливка поверхности surface начиная с pos цветом fill_color.
        Использует get_at/set_at для чтения и записи пикселей.
        """
        x, y = pos
        width, height = surface.get_size()

        # Получаем исходный цвет пикселя
        try:
            target_color = surface.get_at((x, y))[:3]
        except IndexError:
            return

        # Если цвет совпадает с заливкой — ничего делать не нужно
        if self._colors_match(target_color, fill_color[:3]):
            return

        # BFS обход
        queue = deque()
        queue.append((x, y))
        visited = set()
        visited.add((x, y))

        # Блокируем поверхность для быстрого доступа к пикселям
        surface.lock()
        try:
            while queue:
                cx, cy = queue.popleft()
                # Проверяем, что пиксель совпадает с целевым цветом
                if not self._colors_match(surface.get_at((cx, cy))[:3], target_color):
                    continue
                # Устанавливаем новый цвет
                surface.set_at((cx, cy), fill_color)

                # Добавляем соседей
                for nx, ny in [(cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)]:
                    if (0 <= nx < width and 0 <= ny < height and
                            (nx, ny) not in visited):
                        visited.add((nx, ny))
                        queue.append((nx, ny))
        finally:
            surface.unlock()

    def on_mouse_down(self, pos, canvas):
        """Запускает заливку по клику."""
        self.flood_fill(canvas, pos, self.color)
        # Не переходим в режим drawing — заливка мгновенная
