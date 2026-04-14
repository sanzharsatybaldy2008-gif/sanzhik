import os
import pygame
from player import MusicPlayer

pygame.init()
pygame.mixer.init()

WIDTH = 800
HEIGHT = 400

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Music Player")

font = pygame.font.SysFont("arial", 30)
small_font = pygame.font.SysFont("arial", 24)
clock = pygame.time.Clock()

music_folder = os.path.join(os.path.dirname(__file__), "music")
player = MusicPlayer(music_folder)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                player.play()

            elif event.key == pygame.K_s:
                player.pause()

            elif event.key == pygame.K_n:
                player.next_track()

            elif event.key == pygame.K_b:
                player.previous_track()

            elif event.key == pygame.K_q:
                running = False

    screen.fill((240, 240, 240))

    title = font.render("Music Player", True, (0, 0, 0))
    track = small_font.render("Track: " + player.current_track_name(), True, (0, 0, 0))
    pos = small_font.render("Position: " + player.current_position(), True, (0, 0, 0))

    c1 = small_font.render("P = Play", True, (0, 0, 0))
    c2 = small_font.render("S = Pause", True, (0, 0, 0))
    c3 = small_font.render("N = Next", True, (0, 0, 0))
    c4 = small_font.render("B = Previous", True, (0, 0, 0))
    c5 = small_font.render("Q = Quit", True, (0, 0, 0))

    screen.blit(title, (30, 30))
    screen.blit(track, (30, 90))
    screen.blit(pos, (30, 130))

    screen.blit(c1, (30, 210))
    screen.blit(c2, (30, 245))
    screen.blit(c3, (30, 280))
    screen.blit(c4, (30, 315))
    screen.blit(c5, (30, 350))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()