import random

import game_constants as conf
import pygame as pg

from Game.hotel import Hotel
from taxi import Taxi
from parkinglot import ParkingLot
from passenger import Passenger


def is_crashed():
    for x in range(player.player_rect.x, player.player_rect.topright[0], 1):
        for y in range(player.player_rect.y, player.player_rect.bottomleft[1], 1):
            try:
                if sc.get_at((x, y)) in [(220, 215, 177), (155, 144, 122, 255)]:
                    print('crashed')
                    return True
            except:
                print("123")
    if hotel.hotel_rect.colliderect(player.player_rect):
        print('hotel_collide')
        return True

    return False


running = True

img_dict = {
    "bg": pg.image.load('img/Background.png'),
    "player": {
        "rear": pg.image.load('img/cab_rear.png'),
        "left": pg.image.load('img/cab_left.png'),
        "right": pg.image.load('img/cab_right.png'),
        "front": pg.image.load('img/cab_front.png'),
    },
    "hole": pg.image.load('img/hole.png'),
    "hotel": pg.transform.scale(pg.image.load('img/hotel.png'), (80, 80)),
    "passenger": pg.image.load("img/passenger.png"),
    "taxi_background": pg.transform.scale(pg.image.load("img/taxi_background.png"), (80, 45)),
    "parking": pg.transform.scale(pg.image.load("img/parking_lot.png"), (80, 45))
}

player = Taxi(img_dict['player'])

hotel = Hotel(img_dict, conf.HOTEL_POSITIONS)

parking_lot = ParkingLot(img_dict, (hotel.hotel_rect.x, hotel.hotel_rect.y + hotel.hotel_rect.height))

passenger = Passenger(img_dict, (hotel.hotel_rect.x, hotel.hotel_rect.y + hotel.hotel_rect.height))

pg.init()

sc = pg.display.set_mode(conf.size)
timer = pg.time.Clock()

while running:
    pg.display.update()
    sc.blit(img_dict['bg'], (0, 0))
    hotel.draw(sc)
    parking_lot.draw(sc)
    passenger.draw(sc)
    keys = pg.key.get_pressed()
    player.move(keys)
    player.draw(sc)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pg.mouse.get_pos()
            print(mouse_x, mouse_y)

    player.player_rect.clamp_ip(sc.get_rect())
    is_crashed()
    timer.tick(conf.FPS)
    pg.display.update()

pg.quit()
