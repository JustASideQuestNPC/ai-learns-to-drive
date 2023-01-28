import pygame as pg
from json import load
from math import sin, cos, radians

# Import config file
with open('configs.json') as config_file:
    configs = load(config_file)

# Pygame has trouble rotating images around their center for some reason.
def blitRotateCenter(surf, image, topleft, angle) -> None:

    rotated_image = pg.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect)

def rotate_point(point, angle, origin=(0,0)) -> tuple:
    angle = radians(angle)
    x = point[0] - origin[0]
    y = point[1] - origin[1]
    new_x = (x * cos(angle)) - (y * sin(angle))
    new_y = (y * cos(angle)) + (x * sin(angle))
    new_x += origin[0]
    new_y += origin[1]
    return (new_x, new_y)

class Car:
    # Display Constants
    color = configs['car']['color']
    inverted_color = configs['car']['inverted color'] # The 'highlight colliding' debug option changes the colors of objects that are overlapping each other
    length = 20
    width = 12
    show_vectors = configs['debug']['show vectors']
    show_collision = configs['debug']['highlight colliding']

    display_trail = configs['car']['trails']
    ticks_per_segment = 1
    trail_segment_decay = 25
    trail_segments = []

    # Physics constants
    top_speed = configs['car']['top speed']
    acceleration = configs['car']['acceleration']
    braking_force = configs['car']['braking force']
    base_deceleration = configs['car']['base deceleration']
    steering_response = configs['car']['steering response']
    base_grip = configs['car']['base grip']
    angle_snap_threshold = configs['car']['angle snap threshold']
    max_angle_delta = configs['car']['max angle delta']

    # Movement variables
    position = pg.Vector2((0,0))
    velocity = pg.Vector2((0,-1))
    facing_angle = 0
    velocity_angle = 0
    current_speed = 0
    applied_velocity = pg.Vector2((0,0))

    # Collision variables
    hitbox_anchors = [(-width / 2, -length / 2), (width / 2, -length / 2), (width / 2, length / 2), (-width / 2, length / 2)]
    is_colliding = False

    # Constructor
    def __init__(self, window, pos, angle = 0) -> None:
        self.window = window
        self.position.update(pos)
        self.facing_angle = angle
        self.velocity_angle = angle
        self.hitbox_points = [
            (i[0] + self.position.x, i[1] + self.position.y)
            for i in self.hitbox_anchors
        ]

    # Draws the car to the screen
    def display(self, ticks_elapsed) -> None:
        applied_color = self.color
        if self.show_collision and self.is_colliding:
            applied_color = self.inverted_color

        sub_surface = pg.Surface((self.width, self.length), pg.SRCALPHA)
        pg.draw.rect(sub_surface, applied_color,
                    pg.rect.Rect(0, 0, self.width, self.length))
        sub_rect = sub_surface.get_rect()
        sub_rect.center = (self.position.x, self.position.y)
        blitRotateCenter(self.window, sub_surface, sub_rect.topleft, self.facing_angle)

        if self.display_trail:
            if ticks_elapsed % self.ticks_per_segment == 0:
                self.trail_segments.append([sub_surface, sub_rect, self.facing_angle])
            for i, segment in enumerate(self.trail_segments):
                alpha = segment[0].get_alpha()
                alpha -= self.trail_segment_decay
                if alpha <= 0:
                    self.trail_segments.pop(i)
                else:
                    self.trail_segments[i][0].set_alpha(alpha)
                    blitRotateCenter(self.window, segment[0],
                    segment[1].topleft, segment[2])

        # Display debug information (if enabled)
        if self.show_vectors:
            displayed_velocity = pg.Vector2()
            displayed_velocity.from_polar((self.current_speed * 5, -self.velocity_angle - 90))
            pg.draw.line(self.window, '#00ff00', self.position, displayed_velocity + self.position, 2)

    # Moves the car based on physics and control input
    def move(self, throttle, steering) -> None:
        # Calculate acceleration/braking
        if throttle > 0:
            applied_acceleration = self.acceleration * throttle
        elif throttle < 0:
            applied_acceleration = self.braking_force * throttle
        else:
            applied_acceleration = -self.base_deceleration

        self.current_speed += applied_acceleration

        # Steer car
        applied_steering = self.steering_response * steering
        self.facing_angle += applied_steering

        # hehe drift physics go brrrr
        angle_delta = self.facing_angle - self.velocity_angle
        if abs(angle_delta) < self.angle_snap_threshold:
            self.velocity_angle = self.facing_angle
        else:
            if angle_delta < -self.max_angle_delta:
                self.velocity_angle = self.facing_angle - self.max_angle_delta
            elif angle_delta > self.max_angle_delta:
                self.velocity_angle = self.facing_angle + self.max_angle_delta
            else:
                self.velocity_angle += angle_delta * self.base_grip

        # Clamp speed between top speed and 0
        if self.current_speed < 0:
            self.current_speed = 0
        elif self.current_speed > self.top_speed:
            self.current_speed = self.top_speed

        # Apply velocity to car
        self.applied_velocity = self.velocity
        self.applied_velocity = self.applied_velocity.rotate(-self.velocity_angle)
        self.applied_velocity.scale_to_length(self.current_speed)
        self.position += self.applied_velocity

        # Update the hitbox position
        self.hitbox_points = [
            rotate_point((i[0] + self.position.x, i[1] + self.position.y),
            -self.facing_angle, (self.position.x, self.position.y))
            for i in self.hitbox_anchors
        ]