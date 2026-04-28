import pygame
import random

pygame.init()

# Окно
WIDTH = 400
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Practice Racer")

# Цвета
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
GREEN = (0, 150, 0)
BLUE = (0, 100, 255)
RED = (220, 0, 0)
YELLOW = (255, 215, 0)
BLACK = (0, 0, 0)

font = pygame.font.SysFont("Arial", 24)
clock = pygame.time.Clock()

# Дорога
road_x = 100
road_w = 200

# Машина игрока
player_x = 180
player_y = 500
player_w = 40
player_h = 70
player_speed = 7

# Машина врага
enemy_x = random.randint(110, 250)
enemy_y = -100
enemy_w = 40
enemy_h = 70
enemy_speed = 5

# Монета
coin_x = random.randint(120, 280)
coin_y = -50
coin_r = 12

coins = 0
line_y = 0

running = True
while running:
    # Закрытие окна
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Движение игрока
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > road_x:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x + player_w < road_x + road_w:
        player_x += player_speed

    # Враг едет вниз
    enemy_y += enemy_speed
    if enemy_y > HEIGHT:
        enemy_y = -100
        enemy_x = random.randint(110, 250)

    # Монета едет вниз
    coin_y += enemy_speed
    if coin_y > HEIGHT:
        coin_y = -50
        coin_x = random.randint(120, 280)

    # Прямоугольники для столкновения
    player_rect = pygame.Rect(player_x, player_y, player_w, player_h)
    enemy_rect = pygame.Rect(enemy_x, enemy_y, enemy_w, enemy_h)
    coin_rect = pygame.Rect(coin_x - coin_r, coin_y - coin_r, coin_r * 2, coin_r * 2)

    # Столкновение с врагом
    if player_rect.colliderect(enemy_rect):
        running = False

    # Сбор монеты
    if player_rect.colliderect(coin_rect):
        coins += 1
        coin_y = -50
        coin_x = random.randint(120, 280)

    # Движение полос дороги
    line_y += 8
    if line_y > 60:
        line_y = 0

    # Рисование
    screen.fill(GREEN)
    pygame.draw.rect(screen, GRAY, (road_x, 0, road_w, HEIGHT))

    pygame.draw.line(screen, WHITE, (road_x, 0), (road_x, HEIGHT), 5)
    pygame.draw.line(screen, WHITE, (road_x + road_w, 0), (road_x + road_w, HEIGHT), 5)

    for i in range(0, HEIGHT, 60):
        pygame.draw.rect(screen, WHITE, (195, i + line_y, 10, 30))

    pygame.draw.rect(screen, BLUE, (player_x, player_y, player_w, player_h))
    pygame.draw.rect(screen, RED, (enemy_x, enemy_y, enemy_w, enemy_h))
    pygame.draw.circle(screen, YELLOW, (coin_x, coin_y), coin_r)

    text = font.render("Coins: " + str(coins), True, BLACK)
    screen.blit(text, (270, 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()