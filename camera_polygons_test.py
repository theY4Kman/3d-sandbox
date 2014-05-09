"""
Demonstrates a 1D screen of 2D space using polygons for objects. Polygons are
drawn by clicking the left mouse button for the vertices, and ending the last
vertex with the right mouse button.
"""

import math
import os
import random

import pygame
pygame.init()


MOUSEBUTTON_LEFT = 1
MOUSEBUTTON_RIGHT = 3


class CameraScreenPlayground(object):
    """Draws a 1D screen of 2D space"""

    camera_circle_width = 3
    camera_circle_color = (0, 0, 0)

    screen_line_width = 1
    screen_line_color = (50, 50, 50)

    on_screen_color = (0, 0, 255)
    off_screen_color = (255, 0, 0)

    def __init__(self, size, camera=None, screen_size=None,
                 camera_to_screen=90, polygons=None):
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

        self.polygons = polygons
        if self.polygons is None:
            self.polygons = []

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
        self.draw_polygons(surface)
        self.draw_screen_pixels(surface)

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

    def draw_polygons(self, surface):
        for polygon in self.polygons:
            pygame.draw.polygon(surface, polygon.color, polygon.vertices)

    def draw_screen_pixels(self, surface):
        camera_x, camera_y = self.camera
        screen_x = camera_x + self.camera_to_screen

        angle_bounds = {}
        dists = {}
        for polygon in self.polygons:
            angle_bounds[polygon] = polygon.angle_bounds(self.camera)
            dists[polygon] = polygon.min_dist(self.camera)

        for screen_y in xrange(camera_y - self.screen_size,
                               camera_y + self.screen_size + 1):
            polygons = []
            adjacent = screen_x - camera_x
            opposite = screen_y - camera_y
            angle = math.atan2(opposite, adjacent)

            for polygon in self.polygons:
                max_angle, min_angle = angle_bounds[polygon]
                if min_angle <= angle <= max_angle:
                    polygons.append(polygon)

            if polygons:
                # Draw the polygon with a point closest to the camera
                polygon = min(polygons, key=lambda p: dists[p])
                surface.set_at((screen_x, screen_y), polygon.color)


class Sandbox(object):
    def __init__(self, size, padding=10):
        self.size = self.width, self.height = size
        self.padding = padding

        self.camera_test = CameraScreenPlayground(size)
        self.camera_test.polygons += [
            Polygon([
                (200, 100),
                (200, 200),
                (300, 200),
            ], (255, 0, 0))
        ]

        # Copy of polygons already drawn (differentiates one user is drawing)
        self.existing_polygons = self.camera_test.polygons[:]

        self.initialize_click_polygon()
        self.initialize_screen()

    def initialize_screen(self):
        self.screen = pygame.display.set_mode((self.width + self.padding * 2,
                                               self.height + self.padding * 2))
        self.surface = pygame.Surface((self.width, self.height))

    def initialize_click_polygon(self):
        # List of coordinates the user has clicked on, to become a new polygon
        self.click_polygon = Polygon([], self.get_random_color())

    def is_in_board(self, (x, y)):
        return (self.padding < x < self.width + self.padding and
                self.padding < y < self.height + self.padding)

    def get_random_color(self):
        return tuple(random.randint(0, 255) for _ in xrange(3))

    def mainloop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    os._exit(0)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.is_in_board(event.pos):
                        self.click_polygon.vertices.append(event.pos)

                        if len(self.click_polygon.vertices) > 2:
                            all_polygons = (self.existing_polygons +
                                            [self.click_polygon])
                            self.camera_test.polygons = all_polygons

                            if event.button == MOUSEBUTTON_RIGHT:
                                self.existing_polygons = all_polygons
                                self.initialize_click_polygon()

            self.surface.fill((255, 255, 255))
            self.camera_test.render(self.surface)

            self.screen.fill((255, 255, 255))
            self.screen.blit(self.surface, (self.padding, self.padding))

            pygame.display.flip()


class Polygon(object):
    def __init__(self, vertices, color):
        self.vertices = vertices
        self.color = color

    def angle_bounds(self, (camera_x, camera_y)):
        angles = []
        for (x, y) in self.vertices:
            adjacent = x - camera_x
            opposite = y - camera_y
            angle_to_point = math.atan2(opposite, adjacent)
            angles.append(angle_to_point)

        return max(angles), min(angles)

    def min_dist(self, (camera_x, camera_y)):
        dists = []
        for (x, y) in self.vertices:
            dists.append(math.sqrt((x - camera_x) ** 2 + (y - camera_y) ** 2))
        return min(dists)


if __name__ == '__main__':
    sandbox = Sandbox((640, 480))
    sandbox.mainloop()
