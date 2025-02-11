from settings import *
import pygame as pg
import numpy as np


class InputManager:
    def __init__(self, app):
        self.app = app

        # mouse
        self.mouse_pos = None
        self.mouse_state = None
        self.left_click = None
        self.unicode = None

    def update(self):
        self.left_click = False
        self.unicode = None
        self.mouse_pos = pg.mouse.get_pos() * np.array(DIMENSIONS) / np.array(self.app.screen.get_size())
        self.mouse_state = pg.mouse.get_pressed()

        for event in pg.event.get():
            match event.type:
                case pg.QUIT:
                    self.app.running = False

                case pg.VIDEORESIZE:
                    self.app.dimensions = self.app.screen.get_size()

                case pg.MOUSEBUTTONDOWN:
                    match event.button:
                        case 1:
                            self.left_click = True

                case pg.KEYDOWN:
                    match event.key:
                        case pg.K_UP:
                            if self.app.game_logic.running and not self.app.game_logic.paused:
                                self.app.game_logic.player.control.append(1)  # UP

                        case pg.K_RIGHT:
                            if self.app.game_logic.running and not self.app.game_logic.paused:
                                self.app.game_logic.player.control.append(2)  # RIGHT

                        case pg.K_DOWN:
                            if self.app.game_logic.running and not self.app.game_logic.paused:
                                self.app.game_logic.player.control.append(3)  # DOWN

                        case pg.K_LEFT:
                            if self.app.game_logic.running and not self.app.game_logic.paused:
                                self.app.game_logic.player.control.append(4)  # LEFT

                        case pg.K_ESCAPE:
                            if self.app.game_logic.running:
                                self.app.game_logic.paused = not self.app.game_logic.paused

                    self.unicode = event
                    