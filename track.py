import pygame as pg
import shapely
from json import load

with open('configs.json') as config_file:
    configs = load(config_file)

class Track:
    border_color = configs['track']['border color']

    def __init__(self, window, track_data) -> None:
        self.window = window
        self.borders = track_data['borders']
        # Colliders are created on initialization improve performance
        self.border_colliders = [shapely.LineString(i) for i in self.borders]

    def display(self) -> None:
        for segment in self.borders:
            pg.draw.line(self.window, self.border_color, segment[0], segment[1], 2)