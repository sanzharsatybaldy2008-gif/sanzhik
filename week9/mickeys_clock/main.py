import pygame
from clock import load_assets, draw_clock

pygame.init()

screen = pygame.display.set_mode((1200, 700))
pygame.display.set_caption("Mickey Clock")

clock = pygame.time.Clock()
assets = load_assets()

done = False
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    draw_clock(screen, assets)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()