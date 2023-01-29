import pygame as pg
from json import load
from car import Car
from track import Track
from raycaster import Raycaster
from concurrent.futures import ThreadPoolExecutor
from math import sin, cos, radians

population_size = 5

# Import config file
with open('configs.json') as config_file:
    configs = load(config_file)

# Import tracks
with open('tracks.json') as tracks_file:
    tracks = load(tracks_file)

# Loops through all the AI cars and computes collisions for all of them
def do_all_collisions(track, cars) -> list:
    collision_data = []
    for car in cars:
        collision_data.append(track.do_collisions(car.hitbox_points))
    return collision_data

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
cars = [Car(window, track.start_point, 90) for i in range(population_size)]

# Manages raycasts for ai cars
raycasters = [Raycaster(track.start_point, 0) for c in cars]

# Used to only count checkpoints once per lap
passed_checkpoints = [[False for i in track.checkpoints] for c in cars]
num_checkpoints_passed = [0 for c in cars]

while True:
    clock.tick(60)

    keys = pg.key.get_pressed()

    for event in pg.event.get():
        # Close the window when the X is clicked
        if event.type == pg.QUIT:
            pg.quit()
            quit()
    
    ray_distances = []
    for i, rc in enumerate(raycasters):
        rc.position = cars[i].position
        rc.angle = -cars[i].facing_angle - 90
        ray_distances.append(rc.cast(track.border_colliders))
    
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
        collision_thread = executor.submit(do_all_collisions, track, cars)

        for car in cars:
            car.move(throttle_input, steering_input)

        collision_results = collision_thread.result()

        for i, res in enumerate(collision_results):
            cars[i].is_colliding, passed_cp = res
            if passed_cp != -1 and not passed_checkpoints[i][passed_cp]:
                num_checkpoints_passed[i] += 1
                passed_checkpoints[i][passed_cp] = True
                if num_checkpoints_passed[i] == len(passed_checkpoints[i]):
                    num_checkpoints_passed[i] = 0
                    passed_checkpoints[i] = [False for i in passed_checkpoints]

    # Display everything
    window.fill(configs['display']['background color'])
    track.display()
    for car in cars:
        car.display(ticks_passed)

    if configs['debug']['show raycasts']:
        for i, ray in enumerate(ray_distances):
            for dist in ray:
                ray_endpoint = (
                    cos(radians(-cars[i].facing_angle - 90 + configs['training']['ray angles'][i])) * dist + cars[i].position[0],
                    sin(radians(-cars[i].facing_angle - 90 + configs['training']['ray angles'][i])) * dist + cars[i].position[1]
                )
                pg.draw.line(window, '#00ff00', cars[i].position, ray_endpoint, 2)
                pg.draw.circle(window, '#707070', ray_endpoint, 5)

    pg.display.flip()
    ticks_passed += 1