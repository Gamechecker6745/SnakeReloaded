import pygame as pg
import random as rng

from settings import *
from UI import Button
from classes import Snake, Apple
from scenes import GameOver, MainMenu
from utils import load_sprite


class GameLogic:
    def __init__(self, app):
        self.app = app
        self.running = False
        self.paused = False

        self.game_fps = 10
        self.game_dt = 0
        self.game_time = 0

        Snake.snakes.clear()
        Apple.apples.clear()

        self.player = Snake(self.app)
        Apple(self.app)

        self.mode = [0, 2]  # 0 - Classic, 1 - Portal, 2 - Closed, 3 - Open

        self.return_to_menu = Button(self.app, load_sprite('assets/sprites/buttons/main_menu.png', 0.5, scaled=True),
                                     H_HEIGHT + np.array((0, 300)), align=1, linked_scene=MainMenu)

    def reset(self):
        self.__init__(self.app)

    def run(self):
        self.running = True
        if 1 in self.mode:
            Apple(self.app)

        Apple.generate_all()

    def update(self):
        if self.running:
            Apple.render_all()
            Snake.render_all()

            if not self.paused:
                # executes every app tick
                self.game_dt += self.app.delta_time
                self.game_time += self.app.delta_time

                # executes every game tick
                if self.game_dt >= 1 / self.game_fps:
                    self.player.turn()

                    applesEaten = list(map(lambda x: self.player.body[0] == x.pos, Apple.apples))
                    if np.any(applesEaten):
                        if 1 in self.mode:
                            availableApples = [apple for apple in Apple.apples if apple.pos != self.player.body[0]]
                            self.player.body[0] = rng.choice(availableApples).pos.copy()
                        self.snake_eat_apple()

                    self.player.move()

                    self.game_dt = 0

                    if self.player.body[0] in self.player.body[1:]:
                        self.game_over()

                    if 2 in self.mode and (np.any(np.array(self.player.body[0]) < 0) or np.any(np.array(self.player.body[0]) >= MAP_SIZE)):
                        self.game_over()
            else:
                self.pause_layer()

    def pause_layer(self):
        # fade surface
        fade = pg.Surface(DIMENSIONS)
        fade.fill((130, 130, 130))
        fade.set_alpha(100)

        self.app.surface.blit(fade, (0, 0))

        # pause symbol
        pg.draw.rect(self.app.surface, (250, 0, 0),
                     pg.Rect(H_HEIGHT - 35, H_HEIGHT - 50, 20, 100))
        pg.draw.rect(self.app.surface, (250, 0, 0),
                     pg.Rect(H_HEIGHT + 15, H_HEIGHT - 50, 20, 100))

        self.return_to_menu.update()

    def snake_eat_apple(self):
        self.app.AM.sounds['eat'].play()

        # Update sprites
        self.player.grow()
        Apple.generate_all()

    def game_over(self):
        self.running = False
        self.app.AM.sounds['game_over'].play()
        self.app.scene = GameOver(self.app)
