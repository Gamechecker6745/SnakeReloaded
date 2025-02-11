import pygame as pg
pg.init()

from settings import *
from scenes import MainMenu, Settings
from input_manager import InputManager
from audio_manager import AudioManager
from game_logic import GameLogic
from debug import Debug
from leaderboard import Leaderboard
from utils import mode_to_string
from client import Client


class SnakeReloaded:
    def __init__(self):
        self.running = False

        # pygame
        self.surface = pg.Surface(DIMENSIONS)
        self.screen = pg.display.set_mode(DIMENSIONS, pg.RESIZABLE)
        self.dimensions = self.surface.get_size()

        self.global_leaderboards = {}

        pg.display.set_caption(CAPTION)
        pg.display.set_icon(pg.image.load('assets/sprites/icon.ico'))

        # initialise leaderboards
        for game_type in range(0, 2):
            for game_mode in range(2, 4):
                Leaderboard(self, mode_to_string((game_type, game_mode)))

        # time
        self.clock = pg.time.Clock()
        self.run_time = 0
        self.delta_time = None
        self.fps = None

        # Scene
        self.scene = None

        # managers
        self.IM: InputManager = InputManager(self)
        self.AM: AudioManager = AudioManager(self)
        self.game_logic: GameLogic = GameLogic(self)
        self.debug: Debug = Debug(self)
        self.client: Client = Client(self)

    def run(self):
        self.running = True
        self.scene = MainMenu(self)
        self.client.connect_to_server()
        self.AM.play_music('background')

        while self.running:
            self.update()
        self.on_exit()

    def update(self):
        final_surface = pg.transform.scale(self.surface, self.dimensions)
        self.screen.blit(final_surface, (0, 0))

        self.delta_time = self.clock.tick(FRAMERATE) / 1000
        self.run_time += self.delta_time
        self.fps = self.clock.get_fps()

        self.IM.update()
        self.AM.update()
        self.scene.update()
        self.game_logic.update()
        self.client.update()
        self.debug.update() if DEBUG else None

        pg.display.flip()

    def on_exit(self):
        pg.quit()
        Leaderboard.uploadData()
        Settings.upload_data(self)
        self.client.on_exit()


if __name__ == '__main__':
    app = SnakeReloaded()
    app.run()
