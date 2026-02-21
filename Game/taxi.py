import game_constants as const

import pygame as pg


class Taxi:
    def __init__(self, img_dict, player_view='rear'):
        self.obj_condition = img_dict
        self.player_view = player_view
        self.player_rect = self.obj_condition[player_view].get_rect()
        self.player_rect.x = 300
        self.player_rect.y = 300
        self.player_speed = const.PLAYER_SPEED
        self.x_direction = 0
        self.y_direction = 0

    def move(self, keys):
        self.x_direction = 0
        self.y_direction = 0

        if keys[pg.K_UP]:
            self.y_direction = -1
            self.player_view = "rear"
        elif keys[pg.K_DOWN]:
            self.y_direction = 1
            self.player_view = "front"
        elif keys[pg.K_RIGHT]:
            self.x_direction = 1
            self.player_view = "right"
        elif keys[pg.K_LEFT]:
            self.x_direction = -1
            self.player_view = "left"

        self.player_rect.x += self.player_speed * self.x_direction
        self.player_rect.y += self.player_speed * self.y_direction

    def draw(self, surface):
        surface.blit(self.obj_condition[self.player_view], self.player_rect)
