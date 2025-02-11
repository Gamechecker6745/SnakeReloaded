import pygame as pg
import json

from settings import *
from UI import Button, Text, TextBox, Slider
from utils import load_sprite, generate_checkerboard, time_string, mode_to_string
from leaderboard import Leaderboard


class BaseScene:
    def __init__(self, app):
        self.app = app
        self.background: pg.Surface = pg.Surface(DIMENSIONS)
        self.updated_objs = []

    def update(self):
        self.app.surface.blit(self.background, (0, 0))
        [obj.update() for obj in self.updated_objs]

    def __str__(self):
        return self.__class__.__name__


class MainMenu(BaseScene):
    def __init__(self, app):
        super().__init__(app)
        self.app.game_logic.reset()
        Leaderboard.new_round()

        if self.app.client.in_room:
            self.app.client.leave_room()

        self.background = load_sprite('assets/sprites/backgrounds/main_menu.png', DIMENSIONS)

        self.updated_objs = [Button(self.app, load_sprite('assets/sprites/buttons/start_button.png', 0.5, scaled=True),
                                    CENTRE, align=1, linked_scene=SelectGameType),
                             Button(self.app,
                                    load_sprite('assets/sprites/buttons/settings_button.png', 0.5, scaled=True),
                                    CENTRE + np.array((0, 150)), align=1, linked_scene=Settings),
                             Button(self.app,
                                    load_sprite('assets/sprites/buttons/leaderboard_button.png', 0.5, scaled=True),
                                    CENTRE + np.array((0, 300)), align=1, linked_scene=LeaderboardScene),
                             Button(self.app,
                                    load_sprite('assets/sprites/WIP.png', 3, scaled=True),
                                    CENTRE + np.array((450, 100)), align=1, linked_scene=JoinRoom),
                             Button(self.app,
                                    load_sprite('assets/sprites/WIP.png', 3, scaled=True),
                                    CENTRE + np.array((-450, 100)), align=1, linked_scene=CreateRoom)]


class Settings(BaseScene):
    try:
        with open('cache/settings.json', 'r') as file:
            cache = json.loads(file.read())
    except FileNotFoundError:
        with open('cache/settings.json', 'w') as file:
            file.write(json.dumps({}))
        cache = {}

    @classmethod
    def upload_data(cls, app):
        data = {'volume': app.AM.volume}
        with open('cache/settings.json', 'w') as file:
            file.write(json.dumps(data))

    def __init__(self, app):
        super().__init__(app)
        self.background = load_sprite('assets/sprites/backgrounds/settings_background.png', DIMENSIONS)

        self.updated_objs = [Button(self.app, load_sprite('assets/sprites/buttons/main_menu.png', 0.5, scaled=True),
                                    CENTRE + np.array((0, 400)), align=1, linked_scene=MainMenu),
                             Text(self.app, 'Volume', 'heading', CENTRE + np.array((0, -100)), (255, 255, 0), 1),
                             Slider(self.app, CENTRE + np.array((0, 50)), (50, 50, 50), (255, 255, 255), (400, 100), (0, 1), self.app.AM.volume, link=self.app.AM.update_volume)]


class LeaderboardScene(BaseScene):
    def __init__(self, app, mode=(0, 2)):
        super().__init__(app)
        self.app.game_logic.mode = list(mode)

        self.using_global_leaderboard = False

        self.app.client.get_global_leaderboard(self.app.game_logic.mode)
        leaderboard = Leaderboard.instances[mode_to_string(self.app.game_logic.mode)]
        leaderboard.set_position((H_WIDTH, 0), 1)

        self.background = load_sprite('assets/sprites/backgrounds/snake_background.png', DIMENSIONS, scaled=False)

        self.updated_objs = [leaderboard,
                             Button(self.app, load_sprite('assets/sprites/buttons/main_menu.png', 0.5, scaled=True),
                                    CENTRE + np.array((0, 410)), align=1, linked_scene=MainMenu),
                             Button(self.app, load_sprite('assets/sprites/buttons/open_leaderboard.png', 0.3, scaled=True),
                                    CENTRE + np.array((-130, -350)), align=1, linked_scene=LeaderboardScene, args=((self.app.game_logic.mode[0], 3),)),
                             Button(self.app, load_sprite('assets/sprites/buttons/closed_leaderboard.png', 0.3, scaled=True),
                                    CENTRE + np.array((130, -350)), align=1, linked_scene=LeaderboardScene, args=((self.app.game_logic.mode[0], 2),)),
                             Button(self.app, load_sprite('assets/sprites/buttons/classic_leaderboard.png', 0.3, scaled=True),
                                    CENTRE + np.array((-130, -450)), align=1, linked_scene=LeaderboardScene, args=((0, self.app.game_logic.mode[1]),)),
                             Button(self.app, load_sprite('assets/sprites/buttons/portal_leaderboard.png', 0.3, scaled=True),
                                    CENTRE + np.array((130, -450)), align=1, linked_scene=LeaderboardScene, args=((1, self.app.game_logic.mode[1]),))]

        if 0 in mode:
            self.updated_objs[4].selected = True
        if 1 in mode:
            self.updated_objs[5].selected = True
        if 2 in mode:
            self.updated_objs[3].selected = True
        if 3 in mode:
            self.updated_objs[2].selected = True

    def update(self):
        if not self.using_global_leaderboard and self.app.client.online:
            leaderboard = self.app.global_leaderboards.get(mode_to_string(self.app.game_logic.mode))

            if leaderboard:
                leaderboard.set_position((H_WIDTH, 0), 1)
                self.using_global_leaderboard = True
                self.updated_objs.pop(0)
                self.updated_objs.insert(0, leaderboard)
        super().update()


class SelectGameType(BaseScene):
    def __init__(self, app):
        super().__init__(app)
        self.background = load_sprite('assets/sprites/backgrounds/snake_background.png', DIMENSIONS, scaled=False)

        self.updated_objs = [Button(self.app, load_sprite('assets/sprites/buttons/main_menu.png', 0.5, scaled=True),
                                    CENTRE + np.array((0, 400)), align=1, linked_scene=MainMenu),
                             Button(self.app, load_sprite('assets/sprites/buttons/portal.png', 2, scaled=True),
                                    CENTRE + np.array((300, 0)), align=1, linked_scene=SelectGameMode, args=(1,)),
                             Button(self.app, load_sprite('assets/sprites/buttons/classic.png', 2, scaled=True),
                                    CENTRE + np.array((-300, 0)), align=1, linked_scene=SelectGameMode, args=(0,))]


class SelectGameMode(BaseScene):
    def __init__(self, app, game_type):
        super().__init__(app)
        self.app.game_logic.mode[0] = game_type

        self.background = load_sprite('assets/sprites/backgrounds/snake_background.png', DIMENSIONS, scaled=False)

        self.updated_objs = [Button(self.app, load_sprite('assets/sprites/buttons/main_menu.png', 0.5, scaled=True),
                                    CENTRE + np.array((0, 400)), align=1, linked_scene=MainMenu),
                             Button(self.app, load_sprite('assets/sprites/buttons/open.png', 2, scaled=True),
                                    CENTRE + np.array((-300, 0)), align=1, linked_scene=Game, args=(3,)),
                             Button(self.app, load_sprite('assets/sprites/buttons/closed.png', 2, scaled=True),
                                    CENTRE + np.array((300, 0)), align=1, linked_scene=Game, args=(2,))]


class Game(BaseScene):
    def __init__(self, app, game_mode):
        super().__init__(app)
        self.app.game_logic.mode[1] = game_mode

        self.background = pg.Surface(DIMENSIONS)
        self.background.blit(pg.transform.scale(generate_checkerboard(MAP_SIZE), (HEIGHT, HEIGHT)), (0, 0))
        pg.draw.rect(self.background, (61, 133, 69), pg.Rect(HEIGHT, 0, WIDTH - HEIGHT, HEIGHT))

        game_mode_str = str(self.app.game_logic.mode.copy())
        game_mode_str = game_mode_str[1:-1]
        game_mode_str = game_mode_str.replace('0', 'Classic')
        game_mode_str = game_mode_str.replace('1', 'Portal')
        game_mode_str = game_mode_str.replace('2', 'Closed')
        game_mode_str = game_mode_str.replace('3', 'Open')

        self.updated_objs = [
            Text(self.app, f'Game Mode: {game_mode_str}', 'text', (HEIGHT, 0) + np.array((20, 50)), (255, 255, 0), align=0),
            Text(self.app, f'Score: {self.app.game_logic.player.length - 1}', 'text', (HEIGHT, 0) + np.array((20, 120)),
                 (255, 255, 255), align=0),
            Text(self.app, f'Time: {round(self.app.game_logic.game_time, 2)}', 'text', (HEIGHT, 0) + np.array((20, 190)),
                 (255, 255, 255), align=0)
        ]

        self.app.game_logic.run()

    def update(self):
        try:
            if self.app.game_logic.player.length - 1 > Leaderboard.instances[mode_to_string(self.app.game_logic.mode)].data[0][1]:
                hi_score = self.app.game_logic.player.length - 1
            else:
                hi_score = Leaderboard.instances[mode_to_string(self.app.game_logic.mode)].data[0][1]
        except TypeError:
            hi_score = self.app.game_logic.player.length - 1

        self.updated_objs[1:] = [Text(self.app, f'Score: {self.app.game_logic.player.length - 1}', 'text', (HEIGHT, 0) + np.array((20, 120)), (255, 255, 255), align=0),

                                 Text(self.app, f'Time: {time_string(self.app.game_logic.game_time)}', 'text',
                                      (HEIGHT, 0) + np.array((20, 190)),
                                      (255, 255, 255), align=0),
                                 Text(self.app,
                                      f'Hi-Score: {hi_score}', 'text',
                                      (HEIGHT, 0) + np.array((20, 900)),
                                      (255, 255, 255), align=0)]

        super().update()


class GameOver(BaseScene):
    def __init__(self, app):
        super().__init__(app)
        self.using_global_leaderboard = False

        self.background = pg.Surface(DIMENSIONS)
        self.background.blit(load_sprite('assets/sprites/backgrounds/snake_game_over.png', (HEIGHT, HEIGHT), scaled=False), (0, 0))
        pg.draw.rect(self.background, (20, 50, 23), pg.Rect(HEIGHT, 0, WIDTH - HEIGHT, HEIGHT))

        self.app.client.get_global_leaderboard(self.app.game_logic.mode)
        leaderboard = Leaderboard.instances[mode_to_string(self.app.game_logic.mode)]
        leaderboard.set_position((H_WIDTH + H_HEIGHT, 0), align=1)

        def enter_name(text):
            Leaderboard.instances[mode_to_string(self.app.game_logic.mode)].appendToLeaderboard(self.app.game_logic.player.length - 1, text)
            self.app.client.append_to_global_leaderboard(self.app.game_logic.player.length - 1, text, self.app.game_logic.mode)
            self.updated_objs.append(Button(self.app, load_sprite('assets/sprites/buttons/main_menu.png', 0.5, scaled=True),
                                            (H_HEIGHT, H_HEIGHT) + np.array((0, 410)), align=1, linked_scene=MainMenu))

        self.updated_objs = [leaderboard,
                             Text(self.app, f'Score: {self.app.game_logic.player.length - 1}',
                                  'heading', (H_HEIGHT, H_HEIGHT) + np.array((0, -200)), (255, 255, 0), align=1),
                             Text(self.app, f'Time: {time_string(self.app.game_logic.game_time)}', 'subtitle', (H_HEIGHT, H_HEIGHT) + np.array((0, -270)), (255, 255, 255), align=1),
                             TextBox(self.app, (H_HEIGHT, H_HEIGHT), (600, 200), (255, 0, 0), 5, (255, 255, 255), (0, 0, 0), 90, 'Enter name', (230, 230, 230), 1, enter_name)]

    def update(self):
        if not self.using_global_leaderboard and self.app.client.online:
            leaderboard = self.app.global_leaderboards.get(mode_to_string(self.app.game_logic.mode))

            if leaderboard:
                leaderboard.set_position((H_WIDTH + H_HEIGHT, 0), align=1)
                self.using_global_leaderboard = True
                self.updated_objs.pop(0)
                self.updated_objs.insert(0, leaderboard)

        super().update()


class JoinRoom(BaseScene):
    def __init__(self, app):
        super().__init__(app)
        self.background = pg.Surface(DIMENSIONS)
        self.background.blit(load_sprite('assets/sprites/backgrounds/snake_background.png', DIMENSIONS, scaled=False), (0, 0))

        self.updated_objs = [Button(self.app, load_sprite('assets/sprites/buttons/main_menu.png', 0.5, scaled=True),
                                    CENTRE + np.array((0, 410)), align=1, linked_scene=MainMenu)]

        if not self.app.client.online and not self.app.client.attempting_connection:
            self.updated_objs.append(Text(self.app, 'Unable to connect to server :(', 'title', CENTRE, (255, 255, 255), align=1))
            self.app.client.connect_to_server()

    def update(self):
        if self.app.client.attempting_connection:
            self.updated_objs = [Button(self.app, load_sprite('assets/sprites/buttons/main_menu.png', 0.5, scaled=True),
                                        CENTRE + np.array((0, 410)), align=1, linked_scene=MainMenu),
                                 Text(self.app, 'Attempting to connect...', 'title', CENTRE, (255, 255, 255), align=1)]

        elif not self.app.client.online:
            self.updated_objs = [Button(self.app, load_sprite('assets/sprites/buttons/main_menu.png', 0.5, scaled=True),
                                        CENTRE + np.array((0, 410)), align=1, linked_scene=MainMenu),
                                 Text(self.app, 'Unable to connect to server :(', 'title', CENTRE, (255, 255, 255), align=1)]

        else:
            self.updated_objs = [Button(self.app, load_sprite('assets/sprites/buttons/main_menu.png', 0.5, scaled=True),
                                        CENTRE + np.array((0, 410)), align=1, linked_scene=MainMenu),
                                 Text(self.app, 'Connected', 'title', CENTRE, (255, 255, 255), align=1)]

        super().update()


class CreateRoom(BaseScene):
    def __init__(self, app):
        super().__init__(app)
        self.background = pg.Surface(DIMENSIONS)
        self.background.blit(load_sprite('assets/sprites/backgrounds/snake_background.png', DIMENSIONS, scaled=False), (0, 0))

        self.updated_objs = [Button(self.app, load_sprite('assets/sprites/buttons/main_menu.png', 0.5, scaled=True),
                                    CENTRE + np.array((0, 410)), align=1, linked_scene=MainMenu)]

        if not self.app.client.online and not self.app.client.attempting_connection:
            self.updated_objs.append(Text(self.app, 'Unable to connect to server :(', 'title', CENTRE, (255, 255, 255), align=1))
            self.app.client.connect_to_server()

    def update(self):
        if self.app.client.attempting_connection:
            text = 'Attempting to connect...'
        elif not self.app.client.online:
            text = 'Unable to connect to server :('
        else:  # Online
            text = 'Connected'

            if not self.app.client.in_room:
                self.app.client.create_room()
            elif self.app.client.room_code is not None:
                text = f"Room code: {self.app.client.room_code}"

        self.updated_objs = [
            Button(self.app, load_sprite('assets/sprites/buttons/main_menu.png', 0.5, scaled=True),
                   CENTRE + np.array((0, 410)), align=1, linked_scene=MainMenu),
            Text(self.app, text, 'title', CENTRE, (255, 255, 255), align=1)]

        super().update()
