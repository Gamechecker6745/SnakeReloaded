from UI import align_position
from settings import *

import json
import pygame as pg


class Leaderboard:
    instances = {}
    try:
        with open('cache/leaderboards.json') as file:
            readLeaderboards: dict = json.loads(file.read())
    except FileNotFoundError:
        readLeaderboards = None

    @classmethod
    def uploadData(cls):
        compiledLeaderboard = {instance.name: instance.data for instance in cls.instances.values()}
        with open('cache/leaderboards.json', 'w') as file:
            file.write(json.dumps(compiledLeaderboard))

    @classmethod
    def new_round(cls):
        for instance in cls.instances.values():
            instance.newRound()

    def __init__(self, app, name):
        self.app = app
        self.name = name

        self.rank_length = 10

        self.pos = None

        self.data = [[None, None]] * self.rank_length  # [[name, score]] index = rank

        if Leaderboard.readLeaderboards is not None:
            self.data = Leaderboard.readLeaderboards.get(self.name, self.data)
        self.surface = pg.Surface(DIMENSIONS)
        self.surface.set_colorkey((0, 0, 0))

        Leaderboard.instances[self.name] = self

    def set_position(self, new_position, align=0):
        self.pos = align_position(self.surface, new_position, align)[0], new_position[1]

    def appendToLeaderboard(self, score, name):
        cached_data = self.data.copy()

        for idx, data in enumerate(cached_data):
            if data[1] is None or score > data[1]:
                cached_data.insert(idx, [name, score])
                break

        self.data = cached_data[:self.rank_length]

    def update(self):
        self.app.surface.blit(self.surface, self.pos)

    def text_print(self):
        for rank, data in enumerate(self.data):
            print(f'{rank + 1}: {data[0]} - {data[1]}')
