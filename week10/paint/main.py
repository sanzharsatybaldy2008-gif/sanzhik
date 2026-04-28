import pygame  # импорт библиотеки для создания игр
import sys     # для выхода из программы
import math    # для математических вычислений (нужно для треугольника)

pygame.init()  # инициализация pygame (запуск всех модулей)

WIDTH = 1000   # ширина окна
HEIGHT = 700   # высота окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # создание окна
pygame.display.set_caption("Paint")  # название окна
clock = pygame.time.Clock()  # объект для контроля FPS

WHITE = (255, 255, 255)   # белый цвет
BLACK = (0, 0, 0)         # черный цвет
RED = (255, 0, 0)         # красный цвет
GREEN = (0, 180, 0)       # зеленый цвет
BLUE = (0, 0, 255)        # синий цвет
YELLOW = (255, 255, 0)    # желтый цвет
GRAY = (180, 180, 180)    # серый цвет (для панели)

screen.fill(WHITE)  # заливаем экран белым цветом

current_color = BLACK   # текущий цвет рисования
tool = "brush"          # текущий инструмент (по умолчанию кисть)
drawing = False         # флаг рисования (нажата ли мышь)
start_pos = None        # начальная точка фигуры
last_pos = None         # последняя точка (для линии)
brush_size = 5          # размер кисти
eraser_size = 20        # размер ластика

font = pygame.font.SysFont("Verdana", 20)  # шрифт


def draw_ui():
    pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, 50))  # рисуем верхнюю панель

    # текст с подсказками
    info = (
        f"Tool: {tool} | Colors: 1-Black 2-Red 3-Green 4-Blue 5-Yellow | "
        f"B-Brush R-Rect C-Circle E-Eraser S-Square T-RightTriangle U-Equilateral H-Rhombus"
    )

    text = font.render(info, True, BLACK)  # превращаем текст в изображение
    screen.blit(text, (10, 12))  # выводим текст на экран


canvas = pygame.Surface((WIDTH, HEIGHT))  # создаем поверхность для рисования
canvas.fill(WHITE)  # заливаем ее белым цветом


while True:  # главный игровой цикл
    clock.tick(60)  # ограничение FPS до 60

    for event in pygame.event.get():  # обработка событий
        if event.type == pygame.QUIT:  # если нажали крестик
            pygame.quit()  # закрываем pygame
            sys.exit()     # завершаем программу

        if event.type == pygame.KEYDOWN:  # если нажата клавиша

            if event.key == pygame.K_b:
                tool = "brush"  # кисть
            elif event.key == pygame.K_r:
                tool = "rect"   # прямоугольник
            elif event.key == pygame.K_c:
                tool = "circle" # круг
            elif event.key == pygame.K_e:
                tool = "eraser" # ластик
            elif event.key == pygame.K_s:
                tool = "square" # квадрат
            elif event.key == pygame.K_t:
                tool = "right_triangle"  # прямоугольный треугольник
            elif event.key == pygame.K_u:
                tool = "equilateral_triangle"  # равносторонний треугольник
            elif event.key == pygame.K_h:
                tool = "rhombus"  # ромб

            elif event.key == pygame.K_1:
                current_color = BLACK  # выбор цвета
            elif event.key == pygame.K_2:
                current_color = RED
            elif event.key == pygame.K_3:
                current_color = GREEN
            elif event.key == pygame.K_4:
                current_color = BLUE
            elif event.key == pygame.K_5:
                current_color = YELLOW

            elif event.key == pygame.K_DELETE:
                canvas.fill(WHITE)  # очистка холста

        if event.type == pygame.MOUSEBUTTONDOWN:  # нажали мышь
            if event.pos[1] > 50:  # не рисуем на панели
                drawing = True
                start_pos = event.pos  # запоминаем начало
                last_pos = event.pos   # запоминаем последнюю точку

        if event.type == pygame.MOUSEBUTTONUP:  # отпустили мышь
            if drawing and start_pos and event.pos[1] > 50:
                end_pos = event.pos  # конечная точка

                if tool == "rect":
                    x1, y1 = start_pos
                    x2, y2 = end_pos
                    rect = pygame.Rect(min(x1, x2), min(y1, y2),
                                       abs(x2 - x1), abs(y2 - y1))
                    pygame.draw.rect(canvas, current_color, rect, 2)

                elif tool == "circle":
                    x1, y1 = start_pos
                    x2, y2 = end_pos
                    radius = int(((x2 - x1)**2 + (y2 - y1)**2)**0.5)
                    pygame.draw.circle(canvas, current_color, start_pos, radius, 2)

                elif tool == "square":
                    x1, y1 = start_pos
                    x2, y2 = end_pos
                    side = min(abs(x2 - x1), abs(y2 - y1))
                    square = pygame.Rect(x1, y1, side, side)
                    pygame.draw.rect(canvas, current_color, square, 2)

                elif tool == "right_triangle":
                    x1, y1 = start_pos
                    x2, y2 = end_pos
                    points = [(x1, y1), (x1, y2), (x2, y2)]
                    pygame.draw.polygon(canvas, current_color, points, 2)

                elif tool == "equilateral_triangle":
                    x1, y1 = start_pos
                    x2, y2 = end_pos
                    side = abs(x2 - x1)
                    height = int((math.sqrt(3)/2) * side)
                    points = [(x1, y1 + height), (x1 + side, y1 + height), (x1 + side//2, y1)]
                    pygame.draw.polygon(canvas, current_color, points, 2)

                elif tool == "rhombus":
                    x1, y1 = start_pos
                    x2, y2 = end_pos
                    cx = (x1 + x2) // 2
                    cy = (y1 + y2) // 2
                    points = [(cx, y1), (x2, cy), (cx, y2), (x1, cy)]
                    pygame.draw.polygon(canvas, current_color, points, 2)

            drawing = False  # перестали рисовать
            start_pos = None
            last_pos = None

        if event.type == pygame.MOUSEMOTION and drawing:
            if event.pos[1] > 50:
                if tool == "brush":
                    pygame.draw.line(canvas, current_color, last_pos, event.pos, brush_size)
                    last_pos = event.pos

                elif tool == "eraser":
                    pygame.draw.line(canvas, WHITE, last_pos, event.pos, eraser_size)
                    last_pos = event.pos

    screen.fill(WHITE)  # очистка экрана
    screen.blit(canvas, (0, 0))  # вывод холста
    draw_ui()  # рисуем интерфейс

    pygame.display.flip()  # обновляем экран