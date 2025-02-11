from settings import *

import random
import pygame as pg
import numpy as np

from utils import load_sprite


class Snake:
    snakes = []

    @classmethod
    def render_all(cls):
        for snake in cls.snakes:
            snake.render()

    def __init__(self, app):
        self.app = app

        self.luke = load_sprite('assets/sprites/UpdatedSnakeHead.jpg', [self.app.surface.get_height() / MAP_SIZE] * 2)

        self.length = 1
        self.direction = 1
        self.body = [SNAKE_START_POS.copy()]
        self.control = []

        Snake.snakes.append(self)

    def grow(self):
        self.body.append([None, None])
        self.length += 1

    def move(self):
        for idx, coord in enumerate(self.body.copy()[:-1]):
            self.body[idx + 1] = coord[:]

        match self.direction:
            case 1:
                self.body[0][1] -= 1
            case 2:
                self.body[0][0] += 1
            case 3:
                self.body[0][1] += 1
            case 4:
                self.body[0][0] -= 1

        if 3 in self.app.game_logic.mode:
            for idx in range(2):
                if self.body[0][idx] > MAP_SIZE - 1:
                    self.body[0][idx] = 0

                elif self.body[0][idx] < 0:
                    self.body[0][idx] = MAP_SIZE - 1

    def turn(self):
        if len(self.control) > 0:
            direction = self.control.pop(0)
            match direction:
                case 1:
                    if self.direction != 3:
                        self.direction = direction
                    else:
                        self.turn()
                case 2:
                    if self.direction != 4:
                        self.direction = direction
                    else:
                        self.turn()
                case 3:
                    if self.direction != 1:
                        self.direction = direction
                    else:
                        self.turn()
                case 4:
                    if self.direction != 2:
                        self.direction = direction
                    else:
                        self.turn()

    def render(self):
        sprite_size = self.app.surface.get_height() / (2 * MAP_SIZE)
        pg.draw.circle(self.app.surface, (0, 100, 0),
                       [self.body[0][0] * sprite_size * 2 + sprite_size,
                        self.body[0][1] * sprite_size * 2 + sprite_size],
                       sprite_size)

        #self.app.surface.blit(self.luke, [self.body[0][0] * sprite_size * 2 + sprite_size - sprite_size,
        #                                  self.body[0][1] * sprite_size * 2 + sprite_size - sprite_size])

        for idx, part in enumerate(self.body[1:]):
            pg.draw.circle(self.app.surface, (0, 255, 50),
                           [part[0] * sprite_size * 2 + sprite_size,
                            part[1] * sprite_size * 2 + sprite_size],
                           sprite_size * (((self.length - 1) * 2 - (idx + 1)) / ((self.length - 1) * 2)))


class Apple:
    apples = []

    @classmethod
    def render_all(cls):
        for apple in cls.apples:
            apple.render()

    @classmethod
    def generate_all(cls):
        for apple in cls.apples:
            apple.generate()

    def __init__(self, app):
        self.app = app
        self.sprite_size = HEIGHT / (2 * MAP_SIZE)
        self.pos = [0, 0]
        Apple.apples.append(self)

    def render(self):
        pg.draw.circle(self.app.surface, (255, 25, 0),
                       [self.pos[0] * self.sprite_size * 2 + self.sprite_size,
                        self.pos[1] * self.sprite_size * 2 + self.sprite_size], self.sprite_size)

    def generate(self):
        newPos = [random.randint(0, MAP_SIZE - 1), random.randint(0, MAP_SIZE - 1)]
        while newPos in self.app.game_logic.player.body or np.any(list(map(lambda x: newPos == x.pos, Apple.apples))):
            newPos = [random.randint(0, MAP_SIZE - 1), random.randint(0, MAP_SIZE - 1)]

        self.pos = newPos

