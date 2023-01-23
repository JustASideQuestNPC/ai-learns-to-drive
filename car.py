import pygame as pg
import shapely

# Pygame has trouble rotating images around their center for some reason.
def blitRotateCenter(surf, image, topleft, angle):

    rotated_image = pg.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect)


class Car:
    # Display Constants
    color = '#e01616ff'
    length = 35
    width = 20

    display_trail = True
    ticks_per_segment = 1
    trail_segment_decay = 25
    trail_segments = []

    # Physics constants
    top_speed = 10
    acceleration = 0.3
    braking_force = 0.4
    steering_response = 5
    base_grip = 0.07
    angle_snap_threshold = 1
    max_angle_delta = 180

    # Movement variables
    position = pg.Vector2((0,0))
    velocity = pg.Vector2((0,-1))
    facing_angle = 0
    velocity_angle = 0
    current_speed = 0

    # Collision variables
    hitbox = shapely.Polygon(((-width / 2, -length / 2), (width / 2, -length / 2), (width / 2, length / 2), (-width / 2, length / 2)))

    # Constructor
    def __init__(self, window, pos_x, pos_y, angle = 0):
        self.window = window
        self.position.update(pos_x, pos_y)
        self.facing_angle = angle
        self.velocity_angle = angle

    # Draws the car to the screen
    def display(self, ticks_elapsed):
        sub_surface = pg.Surface((self.width, self.length), pg.SRCALPHA)
        pg.draw.rect(sub_surface, self.color,
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

    # Moves the car based on physics and control input
    def move(self, throttle, steering):
        # Calculate acceleration/braking
        if throttle > 0:
            applied_acceleration = self.acceleration * throttle
        elif throttle < 0:
            applied_acceleration = self.braking_force * throttle
        else:
            applied_acceleration = 0

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

        applied_speed = self.velocity
        applied_speed = applied_speed.rotate(-self.velocity_angle)
        applied_speed.scale_to_length(self.current_speed)
        self.position += applied_speed