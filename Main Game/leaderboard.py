from UI import Text, align_position
from utils import string_to_mode
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
    def update_server(cls):
        for instance in cls.instances.values():
            while instance.app.client.attempting_connection:
                pass
            if instance.app.client.online and instance.data[0][0]:
                for name, score in instance.data:
                    if [name, score] != [None, None]:
                        instance.app.client.append_to_global_leaderboard(score, name, string_to_mode(instance.name))
                        instance.__init__(instance.app, instance.name, load_data=False, add_to_class=False)

    @classmethod
    def uploadData(cls):
        compiledLeaderboard = {instance.name: instance.data for instance in cls.instances.values()}
        with open('cache/leaderboards.json', 'w') as file:
            file.write(json.dumps(compiledLeaderboard))

    @classmethod
    def new_round(cls):
        for instance in cls.instances.values():
            instance.newRound()

    def __init__(self, app, name, data=None, add_to_class=True, load_data=True):
        self.app = app
        self.name = name

        self.rank_length = 10

        self.pos = None

        self.triggered = False

        self.recent = None

        self.data = [[None, None]] * self.rank_length if data is None else data  # [[name, score]] index = rank

        if load_data and Leaderboard.readLeaderboards is not None:
            self.data = Leaderboard.readLeaderboards.get(self.name, self.data)
        self.surface = pg.Surface(DIMENSIONS)
        self.surface.set_colorkey((0, 0, 0))
        self.updateSurface()

        if add_to_class:
            Leaderboard.instances[self.name] = self

    def set_position(self, new_position, align=0):
        self.pos = align_position(self.surface, new_position, align)[0], new_position[1]

    def appendToLeaderboard(self, score, name):
        if self.triggered:
            return None

        self.triggered = True
        cached_data = self.data.copy()

        for idx, data in enumerate(cached_data):
            if data[1] is None or score > data[1]:
                cached_data.insert(idx, [name, score])
                self.recent = idx
                break

        self.data = cached_data[:self.rank_length]

        self.updateSurface()

    def newRound(self):
        self.recent = None
        self.triggered = False

        self.updateSurface()

    def updateSurface(self):
        padding = 100

        title_height = 230
        rank_dst = title_height + 40
        separation_dst = 55
        Scores = []
        Nums = []

        Title = Text(self.app, 'Leaderboard:', 'title', (self.surface.get_width() / 2, title_height), (255, 255, 0), align=1)

        for idx, data in enumerate(self.data):
            Nums.append(Text(self.app, str(idx + 1) + ': ', 'subtitle', (H_WIDTH - 150, separation_dst * idx + rank_dst), (255, 255, 0), align=0))

            if data[1] is not None:
                if idx == self.recent:
                    colour = 255, 255, 0
                else:
                    colour = 255, 255, 255

                Scores.append(Text(self.app, str(data[1]) + ' - ' + str(data[0]), 'subtitle', (H_WIDTH - 150 + Nums[idx].surface.get_width(), separation_dst * idx + rank_dst), colour, align=0))

        pg.draw.rect(self.surface, (20, 50, 23),
                     pg.Rect((self.surface.get_width() - Title.surface.get_width() - padding) / 2, 0, Title.surface.get_width() + padding, HEIGHT))

        self.surface.blit(Title.surface, Title.position)

        for rank, score in zip(Nums, Scores):
            self.surface.blit(rank.surface, rank.position)
            self.surface.blit(score.surface, score.position)

    def update(self):
        self.app.surface.blit(self.surface, self.pos)
