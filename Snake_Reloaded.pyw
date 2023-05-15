from copy import copy
import classes as cls
from Sprites import *
from sys import exit
import pygame as pg
import time
import string
import random

pg.init()


def get_events():
    events = []
    for event in pg.event.get():
        if event.type == pg.QUIT:
            events.append('EXIT')
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            events.append('LEFT_CLICK')
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP:
                events.append('UP')
            elif event.key == pg.K_RIGHT:
                events.append('RIGHT')
            elif event.key == pg.K_DOWN:
                events.append('DOWN')
            elif event.key == pg.K_LEFT:
                events.append('LEFT')
            elif event.key == pg.K_ESCAPE:
                events.append('ESCAPE')
            elif event.key == pg.K_RETURN:
                events.append('RETURN')
            elif event.key == pg.K_BACKSPACE:
                events.append('BACKSPACE')
            elif event.key == pg.K_RETURN:
                events.append('RETURN')
            else:
                events.append(['UNICODE', event.unicode])
    return events


def Scale(size: float, value: float, integer=True):
    return round(size * (value / 650)) if integer else size * (value / 650)


class GameEngine:
    def __init__(self,
                 dimensions=(pg.display.get_desktop_sizes()[0][0] - 400, pg.display.get_desktop_sizes()[0][1] - 150)):
        self.dimensions = self.width, self.height = dimensions
        self.display_selected = True
        self.paused = False
        self.game_mode = ['classic', 'open']
        self.activeTextBoxes: list[TextBox] = []
        self.activeText: list[Text] = []
        self.leaderboards = {'classic:open': cls.Leaderboard('classic:open'),
                             'classic:closed': cls.Leaderboard('classic:closed'),
                             'portal:open': cls.Leaderboard('portal:open'),
                             'portal:closed': cls.Leaderboard('portal:closed')}
        self.blit_text = []
        self.framerate = 30
        self.snake: cls.Snake = None
        self.apples: list[cls.Apple] = None
        self.clock = pg.time.Clock()
        self.events = []
        self.loop_funcs = {}
        self.active_buttons: list[Button] = []
        self.sprite_size = self.height / 50
        self.origin = self.h_width, self.h_height = self.width / 2, self.height / 2
        self.background = pg.Surface(self.dimensions)
        self.surface = pg.display.set_mode(self.dimensions)
        pg.display.set_caption('Snake Reloaded')
        pg.display.set_icon(pg.image.load(r'Game_Images\Snake_Icon.ico'))
        Button('Start', pg.image.load('Game_Images/Buttons/Start_Button.png'), Scale(self.height, 0.35, False),
               (255, 255, 255),
               Scale(self.height, 5), self.getGameMode)
        Button('Settings', pg.image.load('Game_Images/Buttons/Settings_Button.png'),
               Scale(self.height, 0.35, False), (255, 255, 255),
               Scale(self.height, 5), self.settings)
        Button('Leaderboard', pg.image.load('Game_Images/Buttons/Leaderboard_Button.png'),
               Scale(self.height, 0.35, False), (255, 255, 255),
               Scale(self.height, 5), self.leaderboard)
        Button('Main_Menu', pg.image.load('Game_Images/Buttons/Main_Menu.png'), Scale(self.height, 0.35, False),
               (255, 255, 255),
               Scale(self.height, 5), self.main_menu)
        Button('Open', pg.image.load('Game_Images/Buttons/Open_Button.png'), Scale(self.height, 1.4, False),
               (255, 255, 255),
               Scale(self.height, 5), self.classic_game, 'open')
        Button('Closed', pg.image.load('Game_Images/Buttons/Closed_Button.png'), Scale(self.height, 1.4, False),
               (255, 255, 255),
               Scale(self.height, 5), self.classic_game, 'closed')
        Button('Classic', pg.image.load('Game_Images/Buttons/Classic.png'), Scale(self.height, 1.4, False),
               (255, 255, 255),
               Scale(self.height, 5), self.getMode, 'classic')
        Button('Portal', pg.image.load('Game_Images/Buttons/Portal.png'), Scale(self.height, 1.4, False),
               (255, 255, 255),
               Scale(self.height, 5), self.getMode, 'portal')
        Button('Open_Leaderboard', pg.image.load('Game_Images/Buttons/Open_Leaderboard.png'),
               Scale(self.height, 0.23, False), (255, 255, 255),
               Scale(self.height, 5), self.leaderboard, [None, 'open'])
        Button('Closed_Leaderboard', pg.image.load('Game_Images/Buttons/Closed_Leaderboard.png'),
               Scale(self.height, 0.23, False),
               (255, 255, 255), Scale(self.height, 5), self.leaderboard,
               [None, 'closed'])
        Button('Portal_Leaderboard', pg.image.load('Game_Images/Buttons/Portal_Leaderboard.png'),
               Scale(self.height, 0.23, False), (255, 255, 255),
               Scale(self.height, 5), self.leaderboard, ['portal', None])
        Button('Classic_Leaderboard', pg.image.load('Game_Images/Buttons/Classic_Leaderboard.png'),
               Scale(self.height, 0.23, False),
               (255, 255, 255), Scale(self.height, 5), self.leaderboard,
               ['classic', None])

        Slider('Volume', self.surface, (0, 0), (50, 50, 50), (255, 255, 255), (300, 100), (0, 100), 50)
        TextBox('name', self.surface, [self.height / 2] * 2, (self.height / 4 * 3, self.height / 4), (255, 0, 0), 5, (255, 255, 255), (0, 0, 0), Scale(self.height, 75), 'Enter name:', (230, 230, 230))
        self.active_sliders: list[Slider] = []

        self.Font = {'Text': pg.font.SysFont("arial", Scale(self.height, 30)),
                     'Title': pg.font.SysFont("comicsansms", Scale(self.height, 72), bold=True),
                     'Subtitle': pg.font.SysFont("comicsansms", Scale(self.height, 32), bold=True)}

        self.Sounds: dict[str: pg.mixer.Sound] = {'Eat': pg.mixer.Sound(r'Game_Sounds\Eat.mp3'),
                                                  'Game_Over': pg.mixer.Sound(r'Game_Sounds\Game_Over.mp3')}

    def get_events(self):
        self.events.clear()
        for event in get_events():
            self.events.append(event)

    def run_buttons(self):
        for button in self.active_buttons:
            button.run(self.surface)
            if button.hovering and 'LEFT_CLICK' in self.events:
                if button.parameters is not None:
                    button.action(button.parameters)
                else:
                    button.action()

    def runTextBoxes(self):
        letter = None
        for textBox in self.activeTextBoxes:
            for event in self.events:
                if event[0] == 'UNICODE':
                    letter = event[1]

            if 'BACKSPACE' in self.events:
                textBox.backspace()
            if 'LEFT' in self.events:
                textBox.move_cursor(False)
            if 'RIGHT' in self.events:
                textBox.move_cursor(True)
            if 'LEFT_CLICK' in self.events:
                textBox.check_for_selection()
            if 'RETURN' in self.events and textBox.get_selected():
                if textBox.name == 'name':
                    winner_name = textBox.get_text()
                    self.leaderboards[f'{self.game_mode[0]}:{self.game_mode[1]}'].appendToLeaderboard(self.snake.score,
                                                                                                      winner_name)
                    Button.buttons['Main_Menu'].set_pos((self.height / 2, self.height - Scale(self.height, 100)))
                    self.active_buttons.append(Button.buttons['Main_Menu'])
            textBox.run(letter)

    def runSliders(self):
        for slider in self.active_sliders:
            slider.draw()

    def main_loop(self):
        while True:
            self.clock.tick(self.framerate)
            self.get_events()
            if 'EXIT' in self.events:
                self.exit_game()

            self.surface.blit(self.background, (0, 0))
            for func, param in self.loop_funcs.items():
                if param is not None:
                    func(param)
                else:
                    func()
            for text in self.activeText:
                text.render(self.surface)
            self.run_buttons()
            self.runTextBoxes()
            self.runSliders()
            pg.display.flip()

    def main_menu(self):
        for sound in self.Sounds.values():
            sound.set_volume(Slider.sliders['Volume'].get_value() / 100)
        self.active_sliders = []
        pg.mouse.set_visible(True)
        self.paused = False
        for leaderboard in self.leaderboards.values():
            leaderboard.newRound()
        self.activeText = []
        self.activeTextBoxes = []
        self.loop_funcs = {}
        self.background = pg.transform.scale(pg.image.load(r'Game_Images\Backgrounds\Snake_Menu.png'),
                                             (self.width, self.height))
        self.active_buttons = [Button.buttons['Start'], Button.buttons['Settings'], Button.buttons['Leaderboard']]
        Button.buttons['Start'].set_pos(self.origin)
        Button.buttons['Settings'].set_pos((self.h_width, self.h_height + Scale(self.height, 100)))
        Button.buttons['Leaderboard'].set_pos((self.h_width, self.h_height + Scale(self.height, 200)))

    def settings(self):
        self.background = pg.transform.scale(pg.image.load(r'Game_Images\Backgrounds\Settings_Background.png'),
                                             (self.width, self.height))
        self.activeText = [Text('VOLUME', self.Font['Title'], (255, 255, 0),
                                (self.h_width, self.h_height / 2 + Scale(self.height, 60)), 'centre')]
        self.active_buttons = [Button.buttons['Main_Menu']]
        Slider.sliders['Volume'].set_pos((self.h_width, self.h_height + Scale(self.height, 40)))
        self.active_sliders = [Slider.sliders['Volume']]
        Button.buttons['Main_Menu'].set_pos((self.h_width, self.height - Scale(self.height, 60)))

    def leaderboard(self, mode=None):
        if mode is not None:
            for idx, gameMode in enumerate(mode):
                if gameMode is not None:
                    self.game_mode[idx] = gameMode

        Button.buttons['Open_Leaderboard'].Selected = self.game_mode[1] == 'open'
        Button.buttons['Closed_Leaderboard'].Selected = self.game_mode[1] != 'open'
        Button.buttons['Portal_Leaderboard'].Selected = self.game_mode[0] == 'portal'
        Button.buttons['Classic_Leaderboard'].Selected = self.game_mode[0] != 'portal'

        self.activeText = []
        self.loop_funcs = {}

        Button.buttons['Portal_Leaderboard'].set_pos((100, 300))
        Button.buttons['Main_Menu'].set_pos((self.h_width, self.height - Scale(self.height, 60)))
        Button.buttons['Classic_Leaderboard'].set_pos((self.h_width - (self.width - self.height) / 2 + Button.buttons['Open_Leaderboard'].size[0] / 2 + Scale(
            self.height, 10),
                                                       Scale(self.height, 40)))
        Button.buttons['Portal_Leaderboard'].set_pos((self.h_width + (self.width - self.height) / 2 -
                                                      Button.buttons['Closed_Leaderboard'].size[0] / 2 - Scale(
            self.height, 10),
                                                      Scale(self.height, 40)))
        Button.buttons['Open_Leaderboard'].set_pos((self.h_width - (self.width - self.height) / 2 +
                                                    Button.buttons['Open_Leaderboard'].size[0] / 2 + Scale(self.height,
                                                                                                           10),
                                                    Scale(self.height, 110)))
        Button.buttons['Closed_Leaderboard'].set_pos((self.h_width + (self.width - self.height) / 2 - Button.buttons['Closed_Leaderboard'].size[0] / 2 - Scale(self.height, 10), Scale(self.height, 110)))

        self.active_buttons = [Button.buttons['Main_Menu'], Button.buttons['Open_Leaderboard'],
                               Button.buttons['Closed_Leaderboard'], Button.buttons['Portal_Leaderboard'],
                               Button.buttons['Classic_Leaderboard']]
        self.background = pg.transform.scale(pg.image.load(r'Game_Images\Backgrounds\Snake_Background.png'),
                                             (self.width, self.height))
        self.leaderboards[f'{self.game_mode[0]}:{self.game_mode[1]}'].draw((self.background, self.Font['Subtitle'],
                                                                            self.Font['Text'], (self.h_width - (self.width - self.height) / 2, 0), False))

    def getGameMode(self):
        self.activeTextBoxes = []
        self.activeText = []
        self.background = pg.transform.scale(pg.image.load(r'Game_Images\Backgrounds\Snake_Background.png'),
                                             (self.width, self.height))
        Button.buttons['Classic'].set_pos((self.width / 3, self.h_height))
        Button.buttons['Portal'].set_pos((self.width / 3 * 2, self.h_height))
        Button.buttons['Main_Menu'].set_pos((self.h_width, self.height - Scale(self.height, 65)))
        self.active_buttons = [Button.buttons['Classic'], Button.buttons['Portal'], Button.buttons['Main_Menu']]

    def getMode(self, gameMode):
        self.game_mode[0] = gameMode
        self.background = pg.transform.scale(pg.image.load(r'Game_Images\Backgrounds\Snake_Background.png'),
                                             (self.width, self.height))
        Button.buttons['Open'].set_pos((self.width / 3, self.h_height))
        Button.buttons['Closed'].set_pos((self.width / 3 * 2, self.h_height))
        Button.buttons['Main_Menu'].set_pos((self.h_width, self.height - Scale(self.height, 65)))
        self.active_buttons = [Button.buttons['Open'], Button.buttons['Closed'], Button.buttons['Main_Menu']]

    def classic_game(self, mode: str):
        pg.mouse.set_visible(False)
        self.snake = cls.Snake()
        cls.Apple.reset()
        self.apples = [cls.Apple(self.height)]
        if self.game_mode[0] == 'portal':
            self.apples.append(cls.Apple(self.height))
        self.game_mode[1] = mode
        current_time = time.perf_counter()
        self.framerate = 10
        [apple.generate(self.snake) for apple in self.apples]
        self.active_buttons = []
        self.loop_funcs = {self.game_mechanics: current_time, self.snake.control: self.events,
                           self.snake.move: self.game_mode[1], self.snake.draw: self.surface,
                           cls.Apple.draw: self.surface}
        self.background = pg.Surface(self.dimensions)
        self.background.blit(pg.transform.scale(pg.image.load(r'Game_Images\Backgrounds\Checkerboard_Background.png'),
                                                (self.height, self.height)), [0, 0])
        pg.draw.rect(self.background, (61, 133, 69), pg.Rect(self.height + 1, 0, self.width - self.height, self.height))

    def game_over(self, duration):
        pg.mouse.set_visible(True)
        self.Sounds['Game_Over'].play()
        self.activeText = [Text(f'Score: {self.snake.score}', self.Font['Title'], (255, 255, 0),
                                (self.h_height, Scale(self.height, 75)), 'centre'),
                           Text(f'Time: {int(duration)}s', self.Font['Subtitle'], (255, 255, 255),
                                (self.h_height, Scale(self.height, 50)), 'centre')]
        self.framerate = 30
        self.loop_funcs = {self.leaderboards[f'{self.game_mode[0]}:{self.game_mode[1]}'].draw: (
            self.background, self.Font['Subtitle'], self.Font['Text'], (self.height, 0), True)}
        self.activeTextBoxes = [TextBox.textBoxes['name']]
        self.background.blit(pg.transform.scale(pg.image.load(r'Game_Images\Backgrounds\Snake_Game_Over.png'),
                                                (self.height, self.height)), (0, 0))

    def game_mechanics(self, start_time):
        hiScore = self.leaderboards[f'{self.game_mode[0]}:{self.game_mode[1]}'].ranks[0]
        try:
            if hiScore < self.snake.score:
                hiScore = self.snake.score
        except TypeError:
            hiScore = 0
        game_duration = time.perf_counter() - start_time
        if not self.paused:
            self.activeText = [
                Text(f'Game Mode: {f"{self.game_mode[0].capitalize()}, {self.game_mode[1].capitalize()}"}',
                     self.Font['Text'], (255, 255, 0),
                     (self.height + Scale(self.height, 25), Scale(self.height, 50))),
                Text(f'Score: {self.snake.score}', self.Font['Text'], (255, 255, 255),
                     (self.height + Scale(self.height, 25), Scale(self.height, 100))),
                Text(f'Time: {round(game_duration, 1)}s', self.Font['Text'], (255, 255, 255),
                     (self.height + Scale(self.height, 25), Scale(self.height, 150))),
                Text(f'Hi-Score: {str(hiScore)}', self.Font['Subtitle'], (0, 60, 0),
                     (self.width - (self.width - self.height) / 2, self.height - Scale(self.height, 100)), 'centre')]
            if self.game_mode[0] == 'classic':
                if self.snake.Body[0] == self.apples[0].coordinates:
                    self.Sounds['Eat'].play()
                    self.snake.grow()
                    self.apples[0].generate(self.snake)
            else:
                for idx, apple in enumerate(self.apples):
                    if self.snake.Body[0] == apple.coordinates:
                        self.Sounds['Eat'].play()
                        self.snake.grow()
                        apple.generate(self.snake)
                        self.snake.Body[0] = copy(self.apples[idx - 1].coordinates)
                        self.apples[idx - 1].generate(self.snake)
                        break

            if self.snake.Body[0] in self.snake.Body[1:]:
                self.game_over(game_duration)

            if self.game_mode[1] == 'closed':
                for coord in range(2):
                    if not (0 <= self.snake.Body[0][coord] < 25):
                        self.game_over(game_duration)
        else:
            pause_surface = pg.Surface(self.dimensions)
            pause_surface.fill((130, 130, 130))
            pause_surface.set_alpha(100)
            self.surface.blit(pause_surface, (0, 0))
            pg.draw.rect(self.surface, (250, 0, 0),
                         pg.Rect(self.height / 2 - Scale(self.height, 35), self.origin[1] - Scale(self.height, 50),
                                 Scale(self.height, 20), Scale(self.height, 100)))
            pg.draw.rect(self.surface, (250, 0, 0),
                         pg.Rect(self.height / 2 + Scale(self.height, 15), self.origin[1] - Scale(self.height, 50),
                                 Scale(self.height, 20), Scale(self.height, 100)))

        if 'ESCAPE' in self.events and pg.mouse.get_focused():
            if self.paused:
                self.framerate = 10
                self.active_buttons = []
                self.loop_funcs = {self.game_mechanics: game_duration, self.snake.control: self.events,
                                   self.snake.move: self.game_mode[1], self.snake.draw: self.surface,
                                   cls.Apple.draw: self.surface}
                self.paused = False
                pg.mouse.set_visible(False)
            else:
                self.pause(game_duration)

       # elif not pg.mouse.get_focused() and not self.paused:
       #    self.pause(game_duration)

    def pause(self, game_duration):
        self.framerate = 30
        self.paused = True
        self.loop_funcs = {self.game_mechanics: game_duration, self.snake.draw: self.surface,
                           cls.Apple.draw: self.surface}

        Button.buttons['Main_Menu'].set_pos((self.height / 2, self.height - Scale(self.height, 100)))
        self.active_buttons = [Button.buttons['Main_Menu']]
        pg.mouse.set_visible(True)

    def exit_game(self):
        cls.Leaderboard.writeToFile()
        exit()


def main():
    Engine = GameEngine()
    Engine.main_menu()
    Engine.main_loop()


if __name__ == '__main__':
    main()
