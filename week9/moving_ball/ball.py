import pygame


class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 25
        self.color = (255, 0, 0)
        self.step = 20

    def move_left(self):
        if self.x - self.radius - self.step >= 0:
            self.x -= self.step

    def move_right(self, screen_width):
        if self.x + self.radius + self.step <= screen_width:
            self.x += self.step

    def move_up(self):
        if self.y - self.radius - self.step >= 0:
            self.y -= self.step

    def move_down(self, screen_height):
        if self.y + self.radius + self.step <= screen_height:
            self.y += self.step

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)