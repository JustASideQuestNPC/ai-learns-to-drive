import pygame as pg
from json import load
from car import *
from track import Track
from concurrent.futures import ThreadPoolExecutor

# Import config file
with open('configs.json') as config_file:
    configs = load(config_file)

# Import tracks
with open('tracks.json') as tracks_file:
    tracks = load(tracks_file)

# Create a window
pg.init()
window = pg.display.set_mode((1080, 720))
pg.display.init()

# Limits framerate/simulation speed to reasonable values
clock = pg.time.Clock()
ticks_passed = 0

# Player car
car = Car(window, 540, 360)

# Current track
track = Track(window, tracks[0])

while True:
    clock.tick(60)

    keys = pg.key.get_pressed()

    for event in pg.event.get():
        # Close the window when the X is clicked
        if event.type == pg.QUIT:
            pg.quit()
            quit()
    
    # Get control input and move the car
    if keys[pg.K_UP] or keys[pg.K_w]:
        throttle_input = 1
    elif keys[pg.K_DOWN] or keys[pg.K_s]:
        throttle_input = -1
    else:
        throttle_input = 0

    if keys[pg.K_LEFT] or keys[pg.K_a]:
        steering_input = 1
    elif keys[pg.K_RIGHT] or keys[pg.K_d]:
        steering_input = -1
    else:
        steering_input = 0

    # Do collision and physics calculations in parallel
    with ThreadPoolExecutor() as executor:
        collision_thread = executor.submit(track.border_collide, car.hitbox_points)
        car.move(throttle_input, steering_input)
        car.is_colliding = collision_thread.result()

    # Display everything
    window.fill(configs['display']['background color'])
    track.display()
    car.display(ticks_passed)
    pg.display.flip()
    ticks_passed += 1