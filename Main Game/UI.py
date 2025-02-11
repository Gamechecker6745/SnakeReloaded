import pygame as pg
import numpy as np

from utils import constrain


def align_position(surface, pos, align):
    match align:
        case 0:
            pass
        case 1:
            pos = pos - np.array(surface.get_size()) / 2
        case 2:
            pos = pos - np.array(surface.get_size())
        case _:
            raise TypeError('Invalid align value')
    return pos


class Button:
    def __init__(self, app, surface: pg.Surface, position, hover_colour=(255, 255, 255), hover_thickness=5,
                 linked_scene=None, align=0, args=None) -> None:
        self.app = app

        self.activated = False
        self.selected = False

        self.dimensions = surface.get_size()
        self.sprite = surface

        self.pos = align_position(self.sprite, position, align)

        self.rect = pg.Rect(self.pos[0], self.pos[1], self.dimensions[0], self.dimensions[1])

        self.linked_scene = linked_scene
        self.args = args

        self.hover_thickness = hover_thickness
        self.hover_colour = hover_colour

    def update(self):
        self.app.surface.blit(self.sprite, self.pos)

        if self.rect.collidepoint(self.app.IM.mouse_pos) or self.selected:
            self.hover()
            if self.app.IM.left_click and not self.selected:
                self.on_click()

    def hover(self):
        pg.draw.rect(self.app.surface, self.hover_colour, self.rect, self.hover_thickness)

    def on_click(self):
        if self.linked_scene is not None:
            if self.args is None:
                self.app.scene = self.linked_scene(self.app)
            else:
                self.app.scene = self.linked_scene(self.app, *self.args)


class Text:
    fonts = {'heading': pg.font.SysFont("comicsansms", 90, bold=True),
             'title': pg.font.SysFont("comicsansms", 70, bold=True),
             'subtitle': pg.font.SysFont("comicsansms", 50),
             'text': pg.font.SysFont("comicsansms", 35),
             'debug': pg.font.SysFont("arial", 30)}

    def __init__(self, app, text, font, position, colour, align=0):
        self.app = app
        self.font = Text.fonts[font]
        self.text = text
        self.colour = colour
        self.surface = self.font.render(self.text, True, self.colour)
        self.position = align_position(self.surface, position, align)

    def update(self):
        self.app.surface.blit(self.surface, self.position)


class TextBox:
    def __init__(self, app,
                 coord: tuple, dimensions: tuple,
                 border_colour: tuple, border_thickness: int,
                 fill_colour: tuple,
                 text_colour: tuple, text_size: int, prompt: str, prompt_colour: tuple, align=0, trigger=None):
        self.app = app
        self.selected = False
        self.trigger = trigger if trigger is not None else lambda x: None

        self.dimensions = dimensions
        self.surface = pg.Surface(dimensions)
        self.top_left_coord = align_position(self.surface, coord, align)

        self.border_colour = border_colour
        self.fill_colour = fill_colour
        self.text_colour = text_colour

        self.text_size = text_size
        self.font = pg.font.SysFont('arial', self.text_size)
        self.text = ''

        self.border_th = border_thickness

        self.rect = pg.Rect(self.top_left_coord[0], self.top_left_coord[1], self.dimensions[0], self.dimensions[1])
        self.inside_rect = pg.Rect(self.rect[0] + self.border_th, self.rect[1] + self.border_th,
                                   self.rect[2] - 2 * self.border_th, self.rect[3] - 2 * self.border_th)

        self.text_blit = (self.inside_rect[0] + self.text_size / 5, self.inside_rect[1] + self.inside_rect[3] / 2 - self.text_size / 2)
        self.text_surface = Text(self.app, self.text, 'subtitle', self.text_blit, self.text_colour)

        self.prompt = Text(self.app, prompt, 'subtitle', self.text_blit, prompt_colour)

        self.cursor_idx = 0
        self.cursor_osc = 0.2
        self.draw_cursor = True
        self.cursor_rect = pg.Rect(0, 0, 0, 0)
        self.cursor_dt = 0

    def select(self):
        self.selected = True

    def check_for_selection(self):
        self.selected = self.rect.collidepoint(self.app.IM.mouse_pos)

    def draw(self):
        pg.draw.rect(self.app.surface, self.border_colour, self.rect)
        pg.draw.rect(self.app.surface, self.fill_colour, self.inside_rect)

        if not self.text:
            self.app.surface.blit(self.font.render(self.prompt.text, True, self.prompt.colour), self.text_blit)

    def backspace(self):
        if self.selected and len(self.text[:self.cursor_idx]) > 0:
            self.cursor_idx -= 1
            new_text = list(self.text)
            new_text.pop(self.cursor_idx)
            self.text = ''.join(new_text)
            self.text_surface = Text(self.app, self.text, 'subtitle', self.text_blit, self.text_colour)

    def cursor(self):
        if self.cursor_dt >= self.cursor_osc:
            self.cursor_dt = 0
            self.draw_cursor = not self.draw_cursor

        if self.draw_cursor and self.selected:
            reduced_text_surface = self.font.render(self.text[:self.cursor_idx], True, self.text_colour)
            self.cursor_rect = pg.Rect(self.inside_rect[0] + reduced_text_surface.get_width() + self.text_size / 5,
                                       self.inside_rect[1] + self.inside_rect[3] / 2 - self.text_size / 2,
                                       self.text_size / 10, self.text_size)
            pg.draw.rect(self.app.surface, self.text_colour, self.cursor_rect)

    def move_cursor(self, forward):
        if forward:
            self.cursor_idx = constrain(self.cursor_idx + 1, (0, len(self.text)), False)

        else:
            self.cursor_idx = constrain(self.cursor_idx - 1, (0, len(self.text)), False)

    def get_selected(self):
        return self.selected

    def type(self):
        if self.selected:
            if self.app.IM.unicode is not None:
                match self.app.IM.unicode.key:
                    case pg.K_RETURN:
                        self.trigger(self.text)

                    case pg.K_BACKSPACE:
                        self.backspace()

                    case pg.K_LEFT:
                        self.move_cursor(False)

                    case pg.K_RIGHT:
                        self.move_cursor(True)

                    case _:
                        if self.app.IM.unicode.unicode:
                            new_text = list(self.text)
                            new_text.insert(self.cursor_idx, self.app.IM.unicode.unicode)
                            self.text = ''.join(new_text)
                            self.cursor_idx += 1

            self.text_surface = Text(self.app, self.text, 'subtitle', self.text_blit, self.text_colour)

            if self.font.render(self.text, True, self.text_colour).get_width() > self.inside_rect[2] - self.text_size / 2.5:
                self.backspace()

        text_surf = self.font.render(self.text, True, self.text_colour)
        self.app.surface.blit(text_surf, self.text_blit)

    def get_text(self):
        return self.text

    def update(self):
        self.cursor_dt += self.app.delta_time
        if self.app.IM.left_click:
            self.selected = self.rect.collidepoint(self.app.IM.mouse_pos)

        self.draw()
        self.cursor()
        self.type()


class Slider:
    sliders = {}

    def __init__(self, app, coordinate: tuple | list, main_colour: tuple | list, slider_colour: tuple | list,
                 dimensions: tuple | list, ranges: tuple | list, default: int, link=None):
        self.app = app
        self.link = link if link is not None else lambda x: None
        self.slider = None
        self.dimensions = dimensions
        self.range = ranges
        self.coord = coordinate
        self.edge_coords = (self.coord[0] - self.dimensions[0] / 2, self.coord[1]), (
            self.coord[0] + self.dimensions[0] / 2, self.coord[1])
        self.colours = main_colour, slider_colour
        self.rect = pg.Rect(self.edge_coords[0][0],
                            self.coord[1] - self.dimensions[1] / 2,
                            self.dimensions[0],
                            self.dimensions[1])
        self.value = default

    def update(self):
        click = pg.mouse.get_pressed()[0]
        mouse_pos = self.app.IM.mouse_pos
        pg.draw.rect(self.app.surface, self.colours[0], self.rect)
        pg.draw.circle(self.app.surface, self.colours[0], self.edge_coords[0], self.dimensions[1] / 2)
        pg.draw.circle(self.app.surface, self.colours[0], self.edge_coords[1], self.dimensions[1] / 2)
        slider_x_coord = ((self.value - self.range[0]) / (self.range[1] - self.range[0])) * self.dimensions[0] + self.edge_coords[0][0]
        self.slider = pg.draw.circle(self.app.surface, self.colours[1], (slider_x_coord, self.coord[1]),
                                     self.dimensions[1] / 2)
        if self.slider.collidepoint(mouse_pos) and click:
            slider_x_coord = constrain(mouse_pos[0], (self.edge_coords[0][0], self.edge_coords[1][0]))
            self.value = (slider_x_coord - self.edge_coords[0][0]) * (self.range[1] - self.range[0]) / self.dimensions[
                0] + self.range[0]

        self.link(self.value)
