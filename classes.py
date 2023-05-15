from Custom.funcs import Scale
import random
import pygame as pg
import json


class Snake:
    def __init__(self):
        self.score = 0
        self.Direction = 1
        self.Body = [[12, 12]]

    def grow(self):
        self.Body.append([None, None])
        self.score += 1

    def control(self, events):
        if 'UP' in events and self.Direction != 3:
            self.Direction = 1
        elif 'RIGHT' in events and self.Direction != 4:
            self.Direction = 2
        elif 'DOWN' in events and self.Direction != 1:
            self.Direction = 3
        elif 'LEFT' in events and self.Direction != 2:
            self.Direction = 4

    def move(self, mode):
        for idx, coord in enumerate(self.Body.copy()[:-1]):
            self.Body[idx + 1] = coord[:]
        if self.Direction == 1:
            self.Body[0][1] -= 1
        elif self.Direction == 2:
            self.Body[0][0] += 1
        elif self.Direction == 3:
            self.Body[0][1] += 1
        else:
            self.Body[0][0] -= 1

        for i in range(2):
            if self.Body[0][i] > 24:
                if mode == 'open':
                    self.Body[0][i] = 0

            elif self.Body[0][i] < 0:
                if mode == 'open':
                    self.Body[0][i] = 24

        return True

    def draw(self, surface):
        sprite_size = surface.get_height() / 50
        if len(self.Body) != 1:
            for idx, part in enumerate(self.Body):
                pg.draw.circle(surface, (0, 255, 50),
                               [part[0] * sprite_size * 2 + sprite_size,
                                part[1] * sprite_size * 2 + sprite_size],
                               sprite_size * (((len(self.Body) - 1) * 2 - idx) / ((len(self.Body) - 1) * 2)))
        pg.draw.circle(surface, (0, 100, 0),
                       [self.Body[0][0] * sprite_size * 2 + sprite_size,
                        self.Body[0][1] * sprite_size * 2 + sprite_size],
                       sprite_size)


class Apple:
    apples = []

    def __init__(self, surface_height):
        self.sprite_size = surface_height / 50
        self.coordinates = [0, 0]
        Apple.apples.append(self)

    def generate(self, snake: Snake):
        self.coordinates[0] = random.randint(0, 24)
        self.coordinates[1] = random.randint(0, 24)
        while self.coordinates in snake.Body:
            self.coordinates[0] = random.randint(0, 24)
            self.coordinates[1] = random.randint(0, 24)

    @classmethod
    def draw(cls, surface):
        for apple in cls.apples:
            pg.draw.circle(surface, (255, 25, 0),
                           [apple.coordinates[0] * apple.sprite_size * 2 + apple.sprite_size,
                            apple.coordinates[1] * apple.sprite_size * 2 + apple.sprite_size], apple.sprite_size)

    @classmethod
    def reset(cls):
        cls.apples.clear()


class Leaderboard:
    instances = []
    try:
        with open('Leaderboards.json') as file:
            string_file = file.read()
        readLeaderboards: dict = json.loads(string_file)
    except FileNotFoundError:
        readLeaderboards = None

    @classmethod
    def writeToFile(cls):
        compiledLeaderboard = {}
        for instance in cls.instances:
            compiledLeaderboard[instance.name] = [instance.ranks, instance.names]
        with open('Leaderboards.json', 'w') as file:
            file.write(json.dumps(compiledLeaderboard))

    def __init__(self, name):
        self.highlight = None
        self.written = False
        Leaderboard.instances.append(self)
        self.name = name
        self.ranks: list = [None] * 10
        self.names: list = [None] * 10
        if Leaderboard.readLeaderboards is not None:
            self.ranks, self.names = Leaderboard.readLeaderboards.get(self.name, [[None] * 10, [None] * 10])
        else:
            self.ranks, self.names = [None] * 10, [None] * 10

    def appendToLeaderboard(self, score, name):
        if not self.written:
            for idx, rank in enumerate(self.ranks):
                if rank is None or score > rank:
                    self.ranks.insert(idx, score)
                    self.names.insert(idx, name)
                    self.highlight = idx
                    break

        self.ranks = self.ranks[:10]
        self.names = self.names[:10]
        self.written = True

    def newRound(self):
        self.written = False
        self.highlight = None

    def draw(self, parameters: list[pg.Surface, pg.font, pg.font, tuple, bool]):
        surface, subtitle, text, pos, game_over = parameters
        size = round(surface.get_width() / 50) * 50
        title_height = Scale(size, 50) if game_over else Scale(size, 90)
        rank_dst = Scale(size, 80) if game_over else Scale(size, 120)
        separation_dst = Scale(size, 25) if game_over else Scale(size, 20)
        Scores = []
        Nums = []
        Title = subtitle.render('Leaderboard:', True, (255, 255, 0))
        for idx, score in enumerate(self.ranks):
            Nums.append(text.render(str(idx + 1) + ': ', True, (255, 255, 0)))
            if score is not None and self.highlight is not None and idx == self.highlight:
                Scores.append(text.render(str(score) + ' - ' + str(self.names[idx]), True, (255, 255, 0)))
            elif score is not None:
                Scores.append(text.render(str(score) + ' - ' + str(self.names[idx]), True, (255, 255, 255)))
        pg.draw.rect(surface, (20, 50, 23),
                     pg.Rect(pos[0] + 1, pos[1], surface.get_width() - surface.get_height(), surface.get_size()[1]))
        surface.blit(Title, (pos[0] + Scale(size, 60), (pos[1] + title_height)))
        for idx, score in enumerate(Scores):
            surface.blit(Nums[idx], (pos[0] + Scale(size, 60), pos[1] + separation_dst * idx + rank_dst))
            surface.blit(score, (pos[0] + Scale(size, 60) + Nums[idx].get_width(), pos[1] + separation_dst * idx + rank_dst))
