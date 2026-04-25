import os
import random
from collections import defaultdict
import numpy as np
import pygame as pg

import game_constants as conf
from Game.hotel import Hotel
from taxi import Taxi
from parkinglot import ParkingLot
from passenger import Passenger
from logger import LoggerRL

pg.init()

font = pg.font.SysFont(None, 48)
sc = pg.display.set_mode(conf.size)
timer = pg.time.Clock()

# ---------------------------------------------------------------------------------

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


def reset_the_game():
    global player, hotel, passenger, parking_lot, game_state

    player = Taxi(img_dict['player'])
    hotel = Hotel(img_dict, conf.HOTEL_POSITIONS)

    lis_hotel_position = list(conf.HOTEL_POSITIONS)
    lis_hotel_position.remove((hotel.hotel_rect.x, hotel.hotel_rect.y))
    choosing_pos_for_passenger = random.choice(lis_hotel_position)

    parking_lot = ParkingLot(img_dict, (hotel.hotel_rect.x, hotel.hotel_rect.y + hotel.hotel_rect.height))
    passenger = Passenger(img_dict, choosing_pos_for_passenger)
    game_state = "PLAYING"


reset_the_game()

# ---------------------------------------------------------------------------------
# Q-learning
actions = [0, 1, 2, 3]
q_table_path = "models/q_tables/q_table.npz"

if os.path.exists(q_table_path):
    data = np.load(q_table_path, allow_pickle=True)
    q_dict = data["q_table"].item()
    Q_table = defaultdict(lambda: [0, 0, 0, 0], q_dict)
else:
    Q_table = defaultdict(lambda: [0, 0, 0, 0])
learning_rate = 0.2
discount_factor = 0.9
#epsilon = 0.3
temperature = 0.6


def choose_action(state, temperature=0.5):
    if random.random() < 0.05:
        return random.choice(actions)
    #else:
    # return np.argmax(Q_table)

    q_values = np.array(Q_table[state])
    q_values = q_values - np.max(q_values)

    probs = np.exp(q_values / temperature)
    probs /= np.sum(probs)

    return np.random.choice(len(q_values), p=probs)


def update_q(state, action, reward, new_state):
    best_option = max(Q_table[new_state])
    Q_table[state][action] += learning_rate * (reward + discount_factor * best_option - Q_table[state][action])


# ---------------------------------------------------------------------------------

def is_crashed():
    for x in range(player.player_rect.x, player.player_rect.topright[0], 1):
        for y in range(player.player_rect.y, player.player_rect.bottomleft[1], 1):
            try:
                if sc.get_at((x, y)) in [(220, 215, 177), (155, 144, 122, 255), (212, 207, 174, 255),
                                         (92, 142, 42, 255), (96, 153, 38, 255)]:
                    return True
            except:
                pass
    if hotel.hotel_rect.colliderect(player.player_rect):
        return True
    return False


# ---------------------------------------------------------------------------------

def make_step():
    global num_of_success, epsilon, temperature
    current_state = get_state()
    action = choose_action(current_state)

    old_x, old_y = player.player_rect.x, player.player_rect.y
    directions = player.auto_move(action)
    player.player_rect.x, player.player_rect.y = directions
    player.player_rect.x = max(0, min(directions[0], conf.size[0] - player.player_rect.width))
    player.player_rect.y = max(0, min(directions[1], conf.size[1] - player.player_rect.height))

    reward = -1
    episode_end = False
    is_success = False

    if is_crashed():
        reward -= 100
        episode_end = True

    if passenger.state == 'waiting':
        goal_x, goal_y = passenger.passenger_rect.x, passenger.passenger_rect.y
    else:
        goal_x, goal_y = parking_lot.parkinglot_rect.x, parking_lot.parkinglot_rect.y

    dist_before = abs(old_x - goal_x) + abs(old_y - goal_y)
    dist_after = abs(player.player_rect.x - goal_x) + abs(player.player_rect.y - goal_y)

    distance_delta = dist_before - dist_after
    reward += distance_delta * 2

    if distance_delta <= 0:
        reward -= 2

    if distance_delta == 0:
        reward -= 3

    if passenger.state == 'waiting' and player.player_rect.colliderect(passenger.passenger_rect):
        passenger.state = "in_taxi"
        reward += 50

    if passenger.state == "in_taxi" and parking_lot.parkinglot_rect.contains(player.player_rect):
        reward += 200
        episode_end = True
        is_success = True
        num_of_success += 1

    next_state = get_state()
    update_q(current_state, action, reward, next_state)


    temperature = max(0.1, temperature * 0.995)

    return episode_end, is_success, reward


print(Q_table)


def get_state():
    if passenger.state == 'waiting':
        goal_x, goal_y = passenger.passenger_rect.x, passenger.passenger_rect.y
    else:
        goal_x, goal_y = parking_lot.parkinglot_rect.x, parking_lot.parkinglot_rect.y

    px, py = player.player_rect.x // 40, player.player_rect.y // 40
    gx, gy = goal_x // 40, goal_y // 40
    return px, py, gx, gy


# ---------------------------------------------------------------------------------

def draw_victory_text(text):
    text_surface = font.render(text, True, conf.BLACK)
    text_rect = text_surface.get_rect(center=(conf.size[0] / 2, conf.size[1] / 2))
    sc.blit(text_surface, text_rect)


num_episodes = 100
max_steps = 100

current_episode = 0
current_step = 0
training_done = False
num_of_success = 0
total_reward = 0

logger = LoggerRL()

reset_the_game()


# training
def play_optimal_path(max_steps=200, step_delay=100):
    reset_the_game()

    for step in range(max_steps):

        state = get_state()
        action = np.argmax(Q_table[state])

        directions = player.auto_move(action)
        player.player_rect.x, player.player_rect.y = directions

        player.player_rect.x = max(0, min(player.player_rect.x, conf.size[0] - player.player_rect.width))
        player.player_rect.y = max(0, min(player.player_rect.y, conf.size[1] - player.player_rect.height))

        if passenger.state == "waiting" and player.player_rect.colliderect(passenger.passenger_rect):
            passenger.state = "in_taxi"

        if passenger.state == "in_taxi" and player.player_rect.colliderect(parking_lot.parkinglot_rect):
            print(f"Успіх за {step + 1} кроків")
            return

        if is_crashed():
            print(f"Crash на кроці {step + 1}")
            return

        # рендер
        sc.blit(img_dict['bg'], (0, 0))
        hotel.draw(sc)
        parking_lot.draw(sc)
        passenger.draw(sc)
        player.draw(sc)
        pg.display.update()
        timer.tick(60)

        pg.time.delay(step_delay)


# Основний цикл гри
running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    sc.blit(img_dict['bg'], (0, 0))
    hotel.draw(sc)
    parking_lot.draw(sc)
    passenger.draw(sc)
    player.draw(sc)

    # --- Q-learning крок (тільки під час тренування) ---
    if not training_done:
        episode_end, is_success, reward = make_step()
        current_step += 1
        total_reward += reward

        if episode_end or current_step >= max_steps:
            logger.log_episode(current_episode, total_reward, current_step, is_success)
            total_reward = 0
            current_episode += 1
            current_step = 0
            reset_the_game()

            if current_episode >= 200:
                logger.save_q_table(Q_table)

            print(f"Episode {current_episode} finished. Success: {is_success}")

        if current_episode >= num_episodes:
            training_done = True
            print("Навчання завершено!")
            draw_victory_text("Навчання завершено")
            pg.display.update()
            print(Q_table)
            print("Кількість успіху:", num_of_success)
            pg.time.delay(2000)
            play_optimal_path(max_steps=200, step_delay=100)

    passenger.update(player, parking_lot)

    pg.display.update()
    timer.tick(conf.FPS)
