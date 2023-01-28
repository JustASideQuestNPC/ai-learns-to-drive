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
    checkpoint_color = configs['track']['checkpoint color']
    checkpoint_collision_color = configs['track']['checkpoint collision color']
    start_point_color = configs['track']['start point color']
    
    # Stores track data
    borders = []
    border_colliders = []
    border_segments_colliding = []

    # Debug constants
    highlight_colliding = configs['debug']['highlight colliding']
    show_checkpoints = configs['debug']['show checkpoints']
    show_start_point = configs['debug']['show start point']

    # Constructor
    def __init__(self, window, track_data) -> None:
        self.window = window
        self.borders = track_data['borders']
        self.checkpoints = track_data['checkpoints']
        self.start_point = track_data['start point']
        # Colliders are created once on initialization to improve performance
        self.border_colliders = [shapely.LineString(i) for i in self.borders]
        self.border_segments_colliding = [False for i in self.borders]
        self.checkpoint_colliders = [shapely.LineString(i) for i in self.checkpoints]
        self.checkpoints_colliding = [False for i in self.checkpoints]

    def do_collisions(self, hitbox):
        return (self.border_collide(hitbox), self.checkpoint_collide(hitbox))

    def border_collide(self, hitbox):
        hitbox_poly = shapely.Polygon(hitbox)
        collision = False
        for i, segment in enumerate(self.border_colliders):
            self.border_segments_colliding[i] = False
            if hitbox_poly.intersects(segment):
                self.border_segments_colliding[i] = True
                collision = True
        return collision

    def checkpoint_collide(self, hitbox):
        hitbox_poly = shapely.Polygon(hitbox)
        collision = False
        for i, checkpoint in enumerate(self.checkpoint_colliders):
            self.checkpoints_colliding[i] = False
            if hitbox_poly.intersects(checkpoint):
                self.checkpoints_colliding[i] = True
                collision = True
        return collision

    # Draws the track to the screen
    def display(self) -> None:
        for i, segment in enumerate(self.borders):
            applied_color = self.border_color
            if self.highlight_colliding and self.border_segments_colliding[i]:
                applied_color = self.border_collision_color
            pg.draw.line(self.window, applied_color, segment[0], segment[1], 2)

        if self.show_checkpoints:
            for i, checkpoint in enumerate(self.checkpoints):
                applied_color = self.checkpoint_color
                if self.highlight_colliding and self.checkpoints_colliding[i]:
                    applied_color = self.checkpoint_collision_color
                pg.draw.line(self.window, applied_color, checkpoint[0], checkpoint[1], 2)