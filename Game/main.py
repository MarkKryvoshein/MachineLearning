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
                if sc.get_at((x, y)) in [(220, 215, 177), (155, 144, 122, 255), (212, 207, 174, 255), (92, 142, 42, 255), (96, 153, 38, 255)]:
                    reset_the_game()

            except:
                print("123")
    if hotel.hotel_rect.colliderect(player.player_rect):
        print('hotel_collide')
        return True

    return False


def draw_victory_text():
    text_surface = font.render("Victory!", True, conf.BLACK)
    text_rect = text_surface.get_rect()
    text_rect.x, text_rect.y = conf.size[0] / 2, conf.size[1] / 2
    sc.blit(text_surface, text_rect)


def get_the_passenger():
    if passenger.passenger_rect.colliderect(player.player_rect) and passenger.state == "waiting":
        passenger.state = "in_taxi"


def put_the_passenger():
    if parking_lot.parkinglot_rect.contains(passenger.passenger_rect) and passenger.state == "in_taxi":
        passenger.state = "delivered"

        passenger.passenger_rect.center = parking_lot.parkinglot_rect.center

        return True
    return False


def reset_the_game():
    global player, hotel, passenger, parking_lot, game_state

    player = Taxi(img_dict['player'])
    hotel = Hotel(img_dict, conf.HOTEL_POSITIONS)

    choosing_pos_for_passenger = random.choice(conf.HOTEL_POSITIONS)

    lis_hotel_position = list(conf.HOTEL_POSITIONS)
    print("До:", lis_hotel_position)
    lis_hotel_position.remove((hotel.hotel_rect.x, hotel.hotel_rect.y))
    print("после:", tuple(lis_hotel_position))
    choosing_pos_for_passenger = random.choice(tuple(lis_hotel_position))

    parking_lot = ParkingLot(img_dict, (hotel.hotel_rect.x, hotel.hotel_rect.y + hotel.hotel_rect.height))
    passenger = Passenger(img_dict, choosing_pos_for_passenger)

    game_state = "PLAYING"


running = True
game_state = "PLAYING"

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

pg.init()
reset_the_game()

font = pg.font.SysFont(None, 48)

sc = pg.display.set_mode(conf.size)
timer = pg.time.Clock()

while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            print(pg.mouse.get_pos())
            print(sc.get_at(pg.mouse.get_pos()))

    if game_state == "PLAYING":

        sc.blit(img_dict['bg'], (0, 0))

        hotel.draw(sc)
        parking_lot.draw(sc)

        keys = pg.key.get_pressed()
        player.move(keys)
        player.player_rect.clamp_ip(sc.get_rect())

        is_crashed()
        get_the_passenger()

        passenger.update(player, parking_lot)

        if put_the_passenger():
            game_state = "WIN"

        player.draw(sc)
        passenger.draw(sc)

    elif game_state == "WIN":
        draw_victory_text()

        keys = pg.key.get_pressed()
        if keys[pg.K_r]:
            reset_the_game()

    pg.display.update() 
    timer.tick(conf.FPS)

pg.quit()
