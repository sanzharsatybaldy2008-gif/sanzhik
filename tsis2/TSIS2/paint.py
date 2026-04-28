"""
Графический редактор «Paint» на Pygame.
Все надписи и комментарии на русском языке.

Управление:
  Клавиши 1/2/3 — размер кисти (2 / 5 / 10 пикселей)
  Ctrl+S        — сохранить холст в PNG
  Escape        — отменить ввод текста
  Enter         — зафиксировать текст
"""

import pygame
import sys
import os
from datetime import datetime

# Импортируем инструменты из модуля tools
from tools import (
    PencilTool, LineTool, RectTool, CircleTool, SquareTool,
    RightTriangleTool, EqTriangleTool, RhombusTool,
    EraserTool, FloodFillTool, TextTool
)

# ──────────────────────────────────────────────
# Константы
# ──────────────────────────────────────────────
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 700
TOOLBAR_WIDTH = 180       # ширина панели инструментов
CANVAS_WIDTH = WINDOW_WIDTH - TOOLBAR_WIDTH
CANVAS_HEIGHT = WINDOW_HEIGHT

# Цвета интерфейса
COLOR_BG = (45, 45, 48)           # фон панели инструментов
COLOR_BTN = (60, 60, 63)          # кнопка
COLOR_BTN_HOVER = (80, 80, 85)    # кнопка при наведении
COLOR_BTN_ACTIVE = (0, 122, 204)  # активная кнопка
COLOR_TEXT = (220, 220, 220)      # текст на панели
COLOR_BORDER = (30, 30, 30)       # граница кнопки
COLOR_CANVAS_BG = (255, 255, 255) # фон холста

# Размеры кисти
BRUSH_SIZES = [2, 5, 10]

# Стандартная палитра из 16 цветов (4×4)
PALETTE = [
    (0,   0,   0),    (128, 128, 128), (255, 255, 255), (192, 192, 192),
    (255,   0,   0),  (128,   0,   0), (255, 165,   0), (128,  64,   0),
    (255, 255,   0),  (128, 128,   0), (0,   255,   0), (0,   128,   0),
    (0,   255, 255),  (0,   128, 128), (0,     0, 255), (0,     0, 128),
]

# Имена инструментов (отображаются на кнопках)
TOOL_NAMES = [
    "Карандаш", "Линия", "Прямоугольник",
    "Круг", "Квадрат", "Тр.прям",
    "Тр.равн", "Ромб", "Ластик",
    "Заливка", "Текст",
]


def make_tools():
    """Создаёт и возвращает словарь экземпляров инструментов."""
    return {
        "Карандаш":       PencilTool(),
        "Линия":          LineTool(),
        "Прямоугольник":  RectTool(),
        "Круг":           CircleTool(),
        "Квадрат":        SquareTool(),
        "Тр.прям":        RightTriangleTool(),
        "Тр.равн":        EqTriangleTool(),
        "Ромб":           RhombusTool(),
        "Ластик":         EraserTool(),
        "Заливка":        FloodFillTool(),
        "Текст":          TextTool(),
    }


# ──────────────────────────────────────────────
# Вспомогательный класс кнопки
# ──────────────────────────────────────────────
class Button:
    """Прямоугольная кнопка с текстом."""

    def __init__(self, rect, label, font):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.font = font
        self.active = False    # выбрана ли эта кнопка
        self.hovered = False   # наведён ли курсор

    def draw(self, surface):
        """Отрисовывает кнопку на поверхности."""
        if self.active:
            bg = COLOR_BTN_ACTIVE
        elif self.hovered:
            bg = COLOR_BTN_HOVER
        else:
            bg = COLOR_BTN

        pygame.draw.rect(surface, bg, self.rect, border_radius=4)
        pygame.draw.rect(surface, COLOR_BORDER, self.rect, 1, border_radius=4)

        # Отрисовываем метку по центру
        text_surf = self.font.render(self.label, True, COLOR_TEXT)
        tx = self.rect.centerx - text_surf.get_width() // 2
        ty = self.rect.centery - text_surf.get_height() // 2
        surface.blit(text_surf, (tx, ty))

    def is_clicked(self, pos):
        """Возвращает True, если pos внутри кнопки."""
        return self.rect.collidepoint(pos)

    def update_hover(self, pos):
        """Обновляет состояние наведения по текущей позиции мыши."""
        self.hovered = self.rect.collidepoint(pos)


# ──────────────────────────────────────────────
# Главное приложение
# ──────────────────────────────────────────────
class PaintApp:
    """Основной класс приложения Paint."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Графический редактор — Paint")

        # Окно и поверхности
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.canvas = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT))
        self.canvas.fill(COLOR_CANVAS_BG)

        # Сохранённая копия холста для отрисовки preview-фигур
        self.canvas_backup = self.canvas.copy()

        # Шрифты
        self.font_btn = pygame.font.SysFont("arial", 13)         # кнопки
        self.font_ui = pygame.font.SysFont("arial", 12)          # подсказки
        self.font_text = pygame.font.SysFont("arial", 20, bold=False)  # текстовый инструмент
        self.font_title = pygame.font.SysFont("arial", 14, bold=True)  # заголовки

        # Инструменты
        self.tools = make_tools()
        self.active_tool_name = "Карандаш"

        # Текущие параметры рисования
        self.current_color = (0, 0, 0)
        self.brush_size_index = 0       # индекс в BRUSH_SIZES
        self.current_size = BRUSH_SIZES[0]

        # Флаги состояния
        self.mouse_on_canvas = False    # курсор над холстом
        self.is_drawing = False         # идёт ли процесс рисования

        # Построение интерфейса
        self._build_ui()

    # ──────────────────────────────────────────
    # Построение UI
    # ──────────────────────────────────────────
    def _build_ui(self):
        """Создаёт все кнопки и вычисляет позиции элементов панели."""
        # Кнопки инструментов — начинаются с y=50 (после заголовка)
        self.tool_buttons = []
        btn_x = 10
        btn_w = 160
        btn_h = 32
        btn_gap = 4
        start_y = 45

        for i, name in enumerate(TOOL_NAMES):
            rect = (btn_x, start_y + i * (btn_h + btn_gap), btn_w, btn_h)
            btn = Button(rect, name, self.font_btn)
            if name == self.active_tool_name:
                btn.active = True
            self.tool_buttons.append(btn)

        # Нижняя граница блока инструментов
        tools_bottom = start_y + len(TOOL_NAMES) * (btn_h + btn_gap) + 10

        # ── Палитра цветов ──
        self.palette_rects = []          # pygame.Rect каждого свотча
        palette_top = tools_bottom + 20  # отступ сверху от кнопок
        swatch_size = 28                 # размер одного цветового прямоугольника
        swatch_gap = 4
        cols = 4
        for idx, color in enumerate(PALETTE):
            col = idx % cols
            row = idx // cols
            rx = 10 + col * (swatch_size + swatch_gap)
            ry = palette_top + row * (swatch_size + swatch_gap)
            self.palette_rects.append(pygame.Rect(rx, ry, swatch_size, swatch_size))

        palette_rows = (len(PALETTE) + cols - 1) // cols
        palette_bottom = palette_top + palette_rows * (swatch_size + swatch_gap) + 10

        # ── Текущий выбранный цвет (крупный прямоугольник) ──
        self.selected_color_rect = pygame.Rect(10, palette_bottom + 5, 50, 50)

        # ── Кнопки размера кисти ──
        size_labels = ["1", "2", "3"]
        self.size_buttons = []
        size_y = palette_bottom + 70
        size_btn_w = 46
        size_btn_h = 30
        size_gap = 5
        for i, label in enumerate(size_labels):
            rx = 10 + i * (size_btn_w + size_gap)
            btn = Button((rx, size_y, size_btn_w, size_btn_h), label, self.font_btn)
            if i == self.brush_size_index:
                btn.active = True
            self.size_buttons.append(btn)

        # ── Нижняя подсказка ──
        self.hint_y = WINDOW_HEIGHT - 60   # y-координата текста подсказки

    # ──────────────────────────────────────────
    # Свойство — текущий инструмент
    # ──────────────────────────────────────────
    @property
    def current_tool(self):
        """Возвращает экземпляр активного инструмента."""
        tool = self.tools[self.active_tool_name]
        # Синхронизируем параметры
        tool.color = self.current_color
        tool.size = self.current_size
        return tool

    # ──────────────────────────────────────────
    # Перевод координат холста
    # ──────────────────────────────────────────
    def _canvas_pos(self, screen_pos):
        """Переводит экранные координаты в координаты холста."""
        return (screen_pos[0] - TOOLBAR_WIDTH, screen_pos[1])

    def _on_canvas(self, screen_pos):
        """Возвращает True, если позиция находится внутри области холста."""
        cx, cy = self._canvas_pos(screen_pos)
        return 0 <= cx < CANVAS_WIDTH and 0 <= cy < CANVAS_HEIGHT

    # ──────────────────────────────────────────
    # Сохранение холста
    # ──────────────────────────────────────────
    def _save_canvas(self):
        """Сохраняет холст в PNG-файл с временной меткой."""
        # Убедимся, что папка существует
        save_dir = os.path.dirname(os.path.abspath(__file__))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(save_dir, f"рисунок_{timestamp}.png")
        pygame.image.save(self.canvas, filename)
        print(f"Холст сохранён: {filename}")
        # Показываем кратковременное уведомление (через заголовок окна)
        pygame.display.set_caption(f"Сохранено: {os.path.basename(filename)}")

    # ──────────────────────────────────────────
    # Смена инструмента
    # ──────────────────────────────────────────
    def _set_tool(self, name):
        """Выбирает инструмент по имени, снимает выделение с остальных."""
        # Завершаем текущий ввод текста, если он активен
        text_tool = self.tools["Текст"]
        if text_tool.active:
            text_tool.active = False
            text_tool.text = ""
            text_tool.drawing = False

        self.active_tool_name = name
        for btn in self.tool_buttons:
            btn.active = (btn.label == name)

    def _set_brush_size(self, index):
        """Устанавливает размер кисти по индексу (0/1/2)."""
        self.brush_size_index = index
        self.current_size = BRUSH_SIZES[index]
        for i, btn in enumerate(self.size_buttons):
            btn.active = (i == index)

    # ──────────────────────────────────────────
    # Нужен ли предварительный просмотр
    # ──────────────────────────────────────────
    def _needs_preview(self):
        """Возвращает True для инструментов, использующих preview-отрисовку."""
        return self.active_tool_name in (
            "Линия", "Прямоугольник", "Круг", "Квадрат",
            "Тр.прям", "Тр.равн", "Ромб"
        )

    # ──────────────────────────────────────────
    # Обработка событий
    # ──────────────────────────────────────────
    def handle_events(self):
        """Обрабатывает все события pygame, возвращает False для выхода."""
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            # ── Выход ──
            if event.type == pygame.QUIT:
                return False

            # ── Нажатие клавиши ──
            elif event.type == pygame.KEYDOWN:
                # Ctrl+S — сохранение
                mods = pygame.key.get_mods()
                if event.key == pygame.K_s and (mods & pygame.KMOD_CTRL):
                    self._save_canvas()

                # Размер кисти клавишами 1 / 2 / 3
                elif event.key == pygame.K_1:
                    self._set_brush_size(0)
                elif event.key == pygame.K_2:
                    self._set_brush_size(1)
                elif event.key == pygame.K_3:
                    self._set_brush_size(2)

                # Обработка ввода текстового инструмента
                elif self.active_tool_name == "Текст":
                    tool = self.tools["Текст"]
                    tool.on_key_down(event, self.canvas, self.font_text)

            # ── Нажатие кнопки мыши ──
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos

                # Клик по кнопкам инструментов
                for btn in self.tool_buttons:
                    if btn.is_clicked(pos):
                        self._set_tool(btn.label)
                        break
                else:
                    # Клик по палитре цветов
                    for idx, rect in enumerate(self.palette_rects):
                        if rect.collidepoint(pos):
                            self.current_color = PALETTE[idx]
                            break
                    else:
                        # Клик по кнопкам размера кисти
                        for i, btn in enumerate(self.size_buttons):
                            if btn.is_clicked(pos):
                                self._set_brush_size(i)
                                break
                        else:
                            # Клик по холсту
                            if self._on_canvas(pos):
                                canvas_pos = self._canvas_pos(pos)
                                # Всегда обновляем резервную копию при новом нажатии
                                self.canvas_backup = self.canvas.copy()
                                tool = self.current_tool
                                tool.on_mouse_down(canvas_pos, self.canvas)
                                self.is_drawing = True

            # ── Движение мыши ──
            elif event.type == pygame.MOUSEMOTION:
                pos = event.pos
                # Обновляем состояние наведения для кнопок
                for btn in self.tool_buttons:
                    btn.update_hover(pos)
                for btn in self.size_buttons:
                    btn.update_hover(pos)

                if self.is_drawing and self._on_canvas(pos):
                    canvas_pos = self._canvas_pos(pos)
                    tool = self.current_tool
                    # Для preview-инструментов — передаём screen_canvas=None
                    tool.on_mouse_move(canvas_pos, self.canvas, None)

            # ── Отпускание кнопки мыши ──
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.is_drawing:
                    pos = event.pos
                    canvas_pos = self._canvas_pos(pos)
                    # Ограничиваем координаты холста
                    canvas_pos = (
                        max(0, min(CANVAS_WIDTH - 1, canvas_pos[0])),
                        max(0, min(CANVAS_HEIGHT - 1, canvas_pos[1]))
                    )
                    tool = self.current_tool
                    tool.on_mouse_up(canvas_pos, self.canvas)
                    self.is_drawing = False

        return True  # продолжаем работу

    # ──────────────────────────────────────────
    # Отрисовка панели инструментов
    # ──────────────────────────────────────────
    def _draw_toolbar(self):
        """Отрисовывает левую панель инструментов."""
        toolbar_rect = pygame.Rect(0, 0, TOOLBAR_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_BG, toolbar_rect)

        # Заголовок
        title = self.font_title.render("Инструменты", True, COLOR_TEXT)
        self.screen.blit(title, (10, 15))

        # Кнопки инструментов
        for btn in self.tool_buttons:
            btn.draw(self.screen)

        # Разделитель
        sep_y = self.palette_rects[0].top - 15
        pygame.draw.line(self.screen, COLOR_BORDER, (5, sep_y), (TOOLBAR_WIDTH - 5, sep_y))

        # Заголовок палитры
        pal_title = self.font_title.render("Палитра", True, COLOR_TEXT)
        self.screen.blit(pal_title, (10, sep_y + 2))

        # Свотчи палитры
        for idx, rect in enumerate(self.palette_rects):
            color = PALETTE[idx]
            pygame.draw.rect(self.screen, color, rect)
            # Граница чуть темнее цвета
            pygame.draw.rect(self.screen, (30, 30, 30), rect, 1)

            # Выделяем текущий цвет маркером
            if color == self.current_color:
                pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)
                pygame.draw.rect(self.screen, (0, 0, 0), rect.inflate(-4, -4), 1)

        # Текущий выбранный цвет (крупный прямоугольник)
        pygame.draw.rect(self.screen, self.current_color, self.selected_color_rect)
        pygame.draw.rect(self.screen, COLOR_BORDER, self.selected_color_rect, 2)
        lbl = self.font_ui.render("Цвет:", True, COLOR_TEXT)
        self.screen.blit(lbl, (self.selected_color_rect.right + 5, self.selected_color_rect.top + 2))

        # Разделитель перед размерами кисти
        sz_sep_y = self.size_buttons[0].rect.top - 12
        pygame.draw.line(self.screen, COLOR_BORDER, (5, sz_sep_y), (TOOLBAR_WIDTH - 5, sz_sep_y))
        sz_title = self.font_title.render("Кисть (1/2/3):", True, COLOR_TEXT)
        self.screen.blit(sz_title, (10, sz_sep_y + 2))

        # Кнопки размера кисти
        for btn in self.size_buttons:
            btn.draw(self.screen)

        # Размеры в пикселях рядом с кнопками
        sizes_label = self.font_ui.render("2px / 5px / 10px", True, (160, 160, 160))
        self.screen.blit(sizes_label, (10, self.size_buttons[0].rect.bottom + 4))

        # Разделитель перед подсказкой
        hint_sep_y = self.hint_y - 12
        pygame.draw.line(self.screen, COLOR_BORDER, (5, hint_sep_y), (TOOLBAR_WIDTH - 5, hint_sep_y))

        # Подсказка сохранения
        hint1 = self.font_ui.render("Ctrl+S — сохранить", True, (160, 200, 160))
        self.screen.blit(hint1, (10, self.hint_y))
        hint2 = self.font_ui.render("Инструмент: " + self.active_tool_name, True, (180, 180, 180))
        self.screen.blit(hint2, (10, self.hint_y + 18))
        hint3 = self.font_ui.render(f"Размер: {self.current_size}px", True, (180, 180, 180))
        self.screen.blit(hint3, (10, self.hint_y + 36))

    # ──────────────────────────────────────────
    # Отрисовка холста с preview
    # ──────────────────────────────────────────
    def _draw_canvas(self):
        """Отрисовывает холст, добавляя preview-фигуру поверх если нужно."""
        mouse_pos = pygame.mouse.get_pos()

        if self.is_drawing and self._needs_preview():
            # Рисуем резервную копию, затем поверх неё — preview
            preview_surf = self.canvas_backup.copy()
            canvas_pos = self._canvas_pos(mouse_pos)
            tool = self.current_tool
            tool.draw_preview(preview_surf, canvas_pos)
            self.screen.blit(preview_surf, (TOOLBAR_WIDTH, 0))
        else:
            self.screen.blit(self.canvas, (TOOLBAR_WIDTH, 0))

        # Индикатор размера кисти — маленький кружок рядом с курсором (кроме текста и заливки)
        mouse_pos_now = pygame.mouse.get_pos()
        if (self._on_canvas(mouse_pos_now) and
                self.active_tool_name not in ("Текст", "Заливка", "Ластик")):
            pygame.draw.circle(
                self.screen,
                self.current_color,
                mouse_pos_now,
                max(1, self.current_size // 2),
                1  # только контур
            )

        # Preview текстового инструмента
        if self.active_tool_name == "Текст":
            text_tool = self.tools["Текст"]
            if text_tool.active:
                # Отрисовываем текст с курсором на экране поверх холста
                # (без записи на холст)
                temp_surf = self.canvas.copy()
                text_tool.draw_cursor_preview(temp_surf, self.font_text)
                self.screen.blit(temp_surf, (TOOLBAR_WIDTH, 0))

    # ──────────────────────────────────────────
    # Граница между панелью и холстом
    # ──────────────────────────────────────────
    def _draw_divider(self):
        """Рисует вертикальную линию-разделитель между панелью и холстом."""
        pygame.draw.line(
            self.screen,
            (20, 20, 20),
            (TOOLBAR_WIDTH, 0),
            (TOOLBAR_WIDTH, WINDOW_HEIGHT),
            2
        )

    # ──────────────────────────────────────────
    # Главный цикл
    # ──────────────────────────────────────────
    def run(self):
        """Запускает главный цикл приложения."""
        clock = pygame.time.Clock()

        while True:
            # Обработка событий
            if not self.handle_events():
                break

            # ── Отрисовка ──
            self.screen.fill((30, 30, 30))   # общий фон
            self._draw_canvas()              # холст (с preview)
            self._draw_toolbar()             # левая панель
            self._draw_divider()             # разделитель

            pygame.display.flip()
            clock.tick(60)   # ограничение FPS

        pygame.quit()
        sys.exit()


# ──────────────────────────────────────────────
# Точка входа
# ──────────────────────────────────────────────
if __name__ == "__main__":
    app = PaintApp()
    app.run()
