import pygame as pg
import numpy as np


def mode_to_string(mode):
    return str(mode[0]) + str(mode[1])


def string_to_mode(string):
    return [int(string[0]), int(string[1])]


def load_sprite(file_path, size, alpha=False, scaled=False):
    sprite = pg.image.load(file_path)
    #sprite = pg.image.load("assets/sprites/UpdatedSnakeHead.jpg") DO NOT UN-COMMENT

    if scaled:
        sprite = pg.transform.scale(sprite, np.array(sprite.get_size()) * size)
    else:
        sprite = pg.transform.scale(sprite, size)

    if alpha:
        sprite.convert_alpha()

    return sprite.convert()


def constrain(value: int | float, constraints: list | tuple, overflow=False):
    if value < constraints[0]:
        if overflow:
            value = constraints[1]
        else:
            value = constraints[0]
    elif value > constraints[1]:
        if overflow:
            value = constraints[0]
        else:
            value = constraints[1]
    return value


def generate_checkerboard(size):
    surface = pg.Surface((size, size))
    for y in range(size):
        for x in range(size):
            pixel = np.array((x, y))
            value = tuple(np.array((x, y)) % 2)
            if value[0] ^ value[1]:
                colour = 0, 0, 0
            else:
                colour = 18 , 18 , 18
            surface.set_at(pixel, colour)
    return surface


def seconds_to_time(seconds: float):
    minutes = seconds // 60
    seconds -= minutes * 60
    return seconds, minutes


def time_string(seconds):
    time = seconds_to_time(seconds)
    return f'{f"{str(int(time[1]))}m " if time[1] > 0 else ""}{round(time[0], 2)}s'
