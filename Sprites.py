import pygame
import time
from Custom import funcs

pygame.init()

class Text:
    def __init__(self, text: str, font: pygame.font, colour: tuple[int], position, position_locale='left'):
        self.text = text
        self.font = font
        self.position = position
        self.colour = colour
        self.surface: pygame.Surface = font.render(self.text, True, self.colour)
        self.h_width, self.h_height = self.origin = self.surface.get_width() / 2, self.surface.get_height() / 2
        if position_locale == 'centre':
            self.position = position[0] - self.h_width, position[1]
        elif position_locale == 'left':
            self.position = position
        elif position_locale == 'right':
            self.position = position[0] - self.surface.get_width(), position[1]
        else:
            raise Exception('Invalid position locale.')


    def render(self, surface: pygame.Surface):
        surface.blit(self.surface, self.position)

    def get_surface(self):
        return self.surface



class Button:
    buttons = {}

    def set_pos(self, pos: tuple[int]) -> None:
        self.pos = (pos[0] - self.size[0] / 2, pos[1] - self.size[1] / 2)
        self.Rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def __init__(self, name, surface: pygame.Surface, scale: float, hover_colour: tuple[int], hover_thickness: int, action, parameters=None) -> None:
        Button.buttons[name] = self
        self.parameters = parameters
        self.action = action
        self.activated = False
        self.hover_thickness = hover_thickness
        self.hover_colour = hover_colour
        self.mouse_pos = None
        self.pos = 0, 0
        self.Scale = scale
        self.Selected = False
        self.img = surface
        self.size = int(self.img.get_width() * self.Scale), int(self.img.get_height() * self.Scale)
        self.img = pygame.transform.scale(self.img, self.size)
        self.Rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        self.hovering = False

    def hover(self, surface):
        self.mouse_pos = pygame.mouse.get_pos()
        self.hovering = self.Rect.collidepoint(self.mouse_pos)
        if self.hovering or self.Selected:
            pygame.draw.rect(surface, self.hover_colour, self.Rect, self.hover_thickness)

    def run(self, surface: pygame.Surface):
        surface.blit(self.img, self.pos)
        self.hover(surface)
        self.activated = True if self.hovering and pygame.mouse.get_pressed()[0] else False


class Slider:
    sliders = {}
    def __init__(self, name, surface, coordinate: tuple | list, main_colour: tuple | list, slider_colour: tuple | list, dimensions: tuple | list, ranges: tuple | list, default: int):
        Slider.sliders[name] = self
        self.slider = None
        self.Dimensions = dimensions
        self.range = ranges
        self.Surface = surface
        self.coord = coordinate
        self.edge_coords = (self.coord[0] - self.Dimensions[0]/2, self.coord[1]), (self.coord[0] + self.Dimensions[0]/2, self.coord[1])
        self.colours = main_colour, slider_colour
        self.Rect = pygame.Rect(self.edge_coords[0][0],
                                self.coord[1] - self.Dimensions[1]/2,
                                self.Dimensions[0],
                                self.Dimensions[1])
        self.value = default

    def draw(self):
        click = pygame.mouse.get_pressed()[0]
        mouse_pos = pygame.mouse.get_pos()
        pygame.draw.rect(self.Surface, self.colours[0], self.Rect)
        pygame.draw.circle(self.Surface, self.colours[0], self.edge_coords[0], self.Dimensions[1] / 2)
        pygame.draw.circle(self.Surface, self.colours[0], self.edge_coords[1], self.Dimensions[1] / 2)
        slider_x_coord = ((self.value - self.range[0]) / (self.range[1] - self.range[0])) * self.Dimensions[0] + self.edge_coords[0][0]
        self.slider = pygame.draw.circle(self.Surface, self.colours[1], (slider_x_coord, self.coord[1]),
                                         self.Dimensions[1] / 2)
        if self.slider.collidepoint(mouse_pos) and click:
            slider_x_coord = funcs.constrain(mouse_pos[0], (self.edge_coords[0][0], self.edge_coords[1][0]))
            self.value = (slider_x_coord - self.edge_coords[0][0]) * (self.range[1] - self.range[0]) / self.Dimensions[0] + self.range[0]

    def get_value(self):
        return self.value

    def set_pos(self, pos: tuple[int]):
        self.coord = pos
        self.edge_coords = (self.coord[0] - self.Dimensions[0] / 2, self.coord[1]), (self.coord[0] + self.Dimensions[0] / 2, self.coord[1])
        self.Rect = pygame.Rect(self.edge_coords[0][0],
                                self.coord[1] - self.Dimensions[1] / 2,
                                self.Dimensions[0],
                                self.Dimensions[1])


class TextBox:
    textBoxes = {}

    def __init__(self, name, surface: pygame.Surface,
                 coord: tuple, dimensions: tuple,
                 border_colour: tuple, border_thickness: int,
                 fill_colour: tuple,
                 text_colour: tuple, text_size: int, prompt: str, prompt_colour: tuple):
        TextBox.textBoxes[name] = self
        self.name = name
        self.cursor_idx = 0
        self.text_size = text_size
        self.font = pygame.font.SysFont('arial', self.text_size)
        self.prompt = prompt
        self.prompt_colour = prompt_colour
        self.prompt_surface = self.font.render(self.prompt, True, self.prompt_colour)
        self.text_colour = text_colour
        self.text = ''
        self.text_surface = self.font.render(self.text, True, self.text_colour)
        self.draw_cursor = True
        self.cursor_switch = time.time()
        self.dimensions = dimensions
        self.border_th = border_thickness
        self.top_left_coord = coord[0] - self.dimensions[0] / 2, coord[1] - self.dimensions[1] / 2
        self.rect = pygame.Rect(self.top_left_coord[0], self.top_left_coord[1], self.dimensions[0], self.dimensions[1])
        self.inside_rect = pygame.Rect(self.rect[0] + self.border_th, self.rect[1] + self.border_th, self.rect[2] - 2 * self.border_th, self.rect[3] - 2 * self.border_th)
        self.text_blit = pygame.Rect(self.inside_rect[0] + self.text_size / 5, self.inside_rect[1] + self.inside_rect[3] / 2 - self.text_size / 2, self.text_size / 10, self.text_size)
        self.surface = surface
        self.cursor_rect = pygame.Rect(0, 0, 0, 0)
        self.border_colour = border_colour
        self.fill_colour = fill_colour
        self.selected = False

    def select(self):
        self.selected = True

    def check_for_selection(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.selected = True
        else:
            self.selected = False

    def draw(self):
        pygame.draw.rect(self.surface, self.border_colour, self.rect)
        pygame.draw.rect(self.surface, self.fill_colour, self.inside_rect)

    def backspace(self):
        if self.selected and len(self.text[:self.cursor_idx]) > 0:
            new_text = list(self.text)
            new_text.pop(self.cursor_idx - 1)
            self.text = ''.join(new_text)
            self.cursor_idx -= 1
            self.text_surface = self.font.render(self.text, True, self.text_colour)

    def cursor(self):
        current_time = time.time()
        if current_time >= self.cursor_switch + 0.4:
            self.cursor_switch = current_time
            self.draw_cursor = not self.draw_cursor

        if self.draw_cursor and self.selected:
            reduced_text_surface = self.font.render(self.text[:self.cursor_idx], True, self.text_colour)
            self.cursor_rect = pygame.Rect(self.inside_rect[0] + reduced_text_surface.get_rect()[2] + self.text_size / 5, self.inside_rect[1] + self.inside_rect[3] / 2 - self.text_size / 2, self.text_size / 10, self.text_size)
            pygame.draw.rect(self.surface, self.text_colour, self.cursor_rect)

    def move_cursor(self, forward):
        if self.selected:
            if forward:
                self.cursor_idx = funcs.constrain(self.cursor_idx + 1, (0, len(self.text)), False)
            else:
                self.cursor_idx = funcs.constrain(self.cursor_idx - 1, (0, len(self.text)), False)

    def get_selected(self):
        return self.selected

    def draw_prompt(self):
        if not self.text:
            self.surface.blit(self.prompt_surface, self.text_blit)

    def type(self, letter):
        if self.selected:
            if letter is not None and letter:
                new_text = list(self.text)
                new_text.insert(self.cursor_idx, letter)
                self.text = ''.join(new_text)
                self.cursor_idx += 1


            self.text_surface = self.font.render(self.text, True, self.text_colour)
            if self.text_surface.get_width() > self.inside_rect[2] - self.text_size / 2.5:
                self.backspace()

        self.surface.blit(self.text_surface, self.text_blit)


    def get_text(self):
        return self.text

    def run(self, letter):
        self.draw()
        self.draw_prompt()
        self.cursor()
        self.type(letter)
