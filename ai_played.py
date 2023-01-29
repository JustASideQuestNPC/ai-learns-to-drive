import pygame as pg
from json import load
from car import Car
from track import Track
from raycaster import Raycaster
from concurrent.futures import ThreadPoolExecutor
from math import sin, cos, radians

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

# Current track
track = Track(window, tracks[0])

# Player car
car = Car(window, track.start_point, 90)

# Manages raycasts for ai cars
raycaster = Raycaster(track.start_point, 0)

# Used to only count checkpoints once per lap
passed_checkpoints = [False for i in track.checkpoints]
num_checkpoints_passed = 0

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
        collision_thread = executor.submit(track.do_collisions, car.hitbox_points)
        car.move(throttle_input, steering_input)
        car.is_colliding, passed_cp = collision_thread.result()
        if passed_cp != -1 and not passed_checkpoints[passed_cp]:
            num_checkpoints_passed += 1
            passed_checkpoints[passed_cp] = True
            if num_checkpoints_passed == len(passed_checkpoints):
                num_checkpoints_passed = 0
                passed_checkpoints = [False for i in passed_checkpoints]

    raycaster.position = car.position
    raycaster.angle = -car.facing_angle - 90
    ray_distances = raycaster.cast(track.border_colliders)

    # Display everything
    window.fill(configs['display']['background color'])
    track.display()
    car.display(ticks_passed)

    if configs['debug']['show raycasts']:
        for i, dist in enumerate(ray_distances):
            ray_endpoint = (
                cos(radians(-car.facing_angle - 90 + configs['training']['ray angles'][i])) * dist + car.position[0],
                sin(radians(-car.facing_angle - 90 + configs['training']['ray angles'][i])) * dist + car.position[1]
            )
            pg.draw.line(window, '#00ff00', car.position, ray_endpoint, 2)
            pg.draw.circle(window, '#707070', ray_endpoint, 5)

    pg.display.flip()
    ticks_passed += 1