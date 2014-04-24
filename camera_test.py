import math
import os
import random

import pygame
import itertools

pygame.init()


class CameraScreenPlayground(object):
    """Draws a 1D screen of 2D space"""

    camera_circle_width = 3
    camera_circle_color = (0, 0, 0)

    screen_line_width = 1
    screen_line_color = (50, 50, 50)

    on_screen_color = (0, 0, 255)
    off_screen_color = (255, 0, 0)

    def __init__(self, size, camera=None, screen_size=None,
                 camera_to_screen=90, points=None):
        self.size = self.width, self.height = size

        self.camera = camera
        # Size of one half of screen
        self.screen_size = screen_size
        # Distance between camera and screen
        self.camera_to_screen = camera_to_screen

        if self.camera is None:
            self.camera = (10, self.height / 2)
        if self.screen_size is None:
            self.screen_size = self.height / 8

        self.points = points
        if self.points is None:
            self.points = []

    def is_on_screen(self, (x, y)):
        adjacent = self.camera_to_screen
        opposite = self.screen_size
        max_screen_angle = math.atan2(opposite, adjacent)

        camera_x, camera_y = self.camera
        adjacent = x - camera_x
        opposite = y - camera_y
        angle_to_point = math.atan2(opposite, adjacent)

        return abs(angle_to_point) < max_screen_angle

    def render(self, surface):
        self.draw_camera(surface)
        self.draw_screen(surface)
        self.draw_points(surface)

    def draw_camera(self, surface):
        pygame.draw.circle(surface, self.camera_circle_color, self.camera,
                           self.camera_circle_width)

    def draw_screen(self, surface):
        camera_x, camera_y = self.camera
        screen_x = camera_x + self.camera_to_screen
        pygame.draw.line(surface, self.screen_line_color,
                         (screen_x, camera_y + self.screen_size),
                         (screen_x, camera_y - self.screen_size),
                         self.screen_line_width)

    def draw_points(self, surface):
        for point in self.points:
            # Didn't quite know how to split this line, chose to keep the
            # values at same vertical
            color = (self.on_screen_color if self.is_on_screen(point) else
                     self.off_screen_color)
            surface.set_at(point, color)


class Sandbox(object):
    def __init__(self, size, padding=10):
        self.size = self.width, self.height = size
        self.padding = padding

        self.camera_test = CameraScreenPlayground(size)

        self.initialize_screen()
        self.randomize_points()

    def initialize_screen(self):
        self.screen = pygame.display.set_mode((self.width + self.padding * 2,
                                               self.height + self.padding * 2))
        self.surface = pygame.Surface((self.width, self.height))

    def randomize_points(self):
        total_points = self.width * self.height
        num_points = random.randint(total_points / 16, total_points / 4)

        x_rand = lambda: random.randint(0, self.width)
        y_rand = lambda: random.randint(0, self.height)

        self.camera_test.points = [(x_rand(), y_rand())
                                   for _ in xrange(num_points)]

    def mainloop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    os._exit(0)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.randomize_points()

            self.surface.fill((255, 255, 255))
            self.camera_test.render(self.surface)

            self.screen.fill((255, 255, 255))
            self.screen.blit(self.surface, (self.padding, self.padding))

            pygame.display.flip()


if __name__ == '__main__':
    sandbox = Sandbox((640, 480))
    sandbox.mainloop()
