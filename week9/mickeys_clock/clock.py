import pygame
import datetime
import os

BASE_DIR = os.path.dirname(__file__)
IMAGES_DIR = os.path.join(BASE_DIR, "images")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


def load_images():
    clock_img = pygame.image.load(os.path.join(IMAGES_DIR, "clock.jpeg")).convert_alpha()
    left_hand = pygame.image.load(os.path.join(IMAGES_DIR, "hand_left.jpeg")).convert_alpha()
    right_hand = pygame.image.load(os.path.join(IMAGES_DIR, "hand_right.jpeg")).convert_alpha()

    clock_img = pygame.transform.scale(clock_img, (800, 600))
    left_hand = pygame.transform.scale(left_hand, (120, 120))
    right_hand = pygame.transform.scale(right_hand, (120, 120))

    return clock_img, left_hand, right_hand


def draw_clock(screen, font, clock_img,  left_hand, right_hand):
    now = datetime.datetime.now()
    minute = now.minute
    second = now.second

    minute_angle = -(minute * 6)
    second_angle = -(second * 6)

    rotated_left = pygame.transform.rotate(left_hand, second_angle)
    rotated_right = pygame.transform.rotate(right_hand, minute_angle)

    screen.fill(WHITE)

    # фон часов
    screen.blit(clock_img, clock_img.get_rect(center=(600, 340)))

    
    # руки
    left_rect = rotated_left.get_rect(center=(575, 300))
    right_rect = rotated_right.get_rect(center=(635, 300))

    screen.blit(rotated_left, left_rect)    # левая рука = секунды
    screen.blit(rotated_right, right_rect)  # правая рука = минуты

    # цифровое время
    text = font.render(now.strftime("%M:%S"), True, BLACK)
    screen.blit(text, text.get_rect(center=(600, 640)))
