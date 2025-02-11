import pygame as pg
from scenes import Settings


class AudioManager:
    def __init__(self, app):
        self.app = app
        self.volume = Settings.cache.get('volume', 0.5)
        self.sounds = {'eat': pg.mixer.Sound('assets/sounds/eat.mp3'),
                       'game_over': pg.mixer.Sound('assets/sounds/game_over.mp3')}

        self.music = {'background': "assets/sounds/background.mp3"}

        self.update_volume(self.volume)

    def update_volume(self, volume):
        self.volume = volume

        for sound in self.sounds.values():
            sound.set_volume(volume)

        pg.mixer.music.set_volume(volume / 2)

    def play_sound(self, sound_name):
        self.sounds[sound_name].play()

    def play_music(self, music_name):
        pg.mixer.music.load(self.music[music_name])
        pg.mixer.music.play(-1)

    def update(self):
        pass
