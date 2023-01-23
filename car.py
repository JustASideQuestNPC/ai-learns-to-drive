import pygame as pg
import pymunk as pm

# Pygame has trouble rotating images around their center for some reason.
def blitRotateCenter(surf, image, topleft, angle):

    rotated_image = pg.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect)


class Car:
    # Display Constants
    color = '#BA1111'

    # Physics constants

    # Constructor
    def __init__(self, pos_x, pos_y):
        pass
