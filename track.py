import pygame as pg
import pymunk
import shapely
from json import load

with open('configs.json') as config_file:
    configs = load(config_file)

class Track:
    # Display constants
    border_color = configs['track']['border color']
    border_collision_color = configs['track']['border collision color']
    
    # Stores track data
    borders = []
    border_colliders = []
    border_segments_colliding = []

    # Debug constants
    highlight_colliding = configs['debug']['highlight colliding']

    # Constructor
    def __init__(self, window, track_data) -> None:
        self.window = window
        self.borders = track_data['borders']
        # Colliders are created once on initialization to improve performance
        self.border_colliders = [shapely.LineString(i) for i in self.borders]
        self.border_segments_colliding = [False for i in self.borders]

    def border_collide(self, hitbox):
        hitbox_poly = shapely.Polygon(hitbox)
        collision = False
        for i, segment in enumerate(self.border_colliders):
            self.border_segments_colliding[i] = False
            if hitbox_poly.intersects(segment):
                self.border_segments_colliding[i] = True
                collision = True
        return collision

    # Draws the track to the screen
    def display(self) -> None:
        for i, segment in enumerate(self.borders):
            applied_color = self.border_color
            if self.highlight_colliding and self.border_segments_colliding[i]:
                applied_color = self.border_collision_color
            pg.draw.line(self.window, applied_color, segment[0], segment[1], 2)