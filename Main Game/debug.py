from settings import *
from UI import Text


class Debug:
    def __init__(self, app):
        self.app = app
        self.fps = None
        self.scene = None
        self.game_mode = None

    def update(self):
        self.fps = Text(self.app, f"FPS: {round(self.app.fps)}", 'debug', (10, HEIGHT - 45), (255, 255, 255))
        self.scene = Text(self.app, f"Scene: {self.app.scene}", 'debug', (10, HEIGHT - 75), (255, 255, 255))
        self.game_mode = Text(self.app, f"GameMode: {self.app.game_logic.mode}", 'debug', (10, HEIGHT - 105), (255, 255, 255))
        self.online = Text(self.app, f"Online?: {self.app.client.online}", 'debug', (10, HEIGHT - 135), (255, 255, 255))

        self.fps.update()
        self.scene.update()
        self.game_mode.update()
        self.online.update()
