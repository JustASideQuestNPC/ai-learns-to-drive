import pygame as pg
import shapely
from json import load
from math import sin, cos, radians

# Import config file
with open('configs.json') as config_file:
    configs = load(config_file)

class Raycaster:
    ray_angles = configs['training']['ray angles']
    ray_length = configs['training']['ray length']
    ray_colliders = []
    position = (0, 0)
    angle = 0
    
    def __init__(self, position, angle) -> None:
        self.position = position
        self.angle = angle

    def cast(self, colliders) -> list:
        self.ray_colliders = [
            shapely.LineString((self.position,
            ((self.position[0] + cos(radians(self.angle + i)) * self.ray_length),
            (self.position[1] + sin(radians(self.angle + i)) * self.ray_length))))
            for i in self.ray_angles
        ]
        self.center = shapely.Point(self.position)
        distances = []
        for ray in self.ray_colliders:
            shortest_distance = self.ray_length
            for collider in colliders:
                if ray.intersects(collider):
                    intersect_point = ray.intersection(collider)
                    distance = self.center.distance(intersect_point)
                    if distance < shortest_distance:
                        shortest_distance = distance
            distances.append(shortest_distance)
        return distances