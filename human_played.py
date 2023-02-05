import pygame as pg
from json import load
from car import *
from track import Track
from concurrent.futures import ThreadPoolExecutor

# Load config file
with open('configs.json', 'r') as config_file:
    configs = load(config_file)

# Load tracks
with open('tracks.json', 'r') as tracks_file:
    tracks = load(tracks_file)

# Create a window
pg.init()
window = pg.display.set_mode((1080, 720))
pg.display.init()
font = pg.font.SysFont('monospace', 24)

# Limits framerate/simulation speed to reasonable values
clock = pg.time.Clock()
ticks_passed = 0

# Current track
track = Track(window, tracks[0])

# Player car
car = Car(window, track.start_point, 90)

# Used to only count checkpoints once per lap
passed_checkpoints = [False for i in track.checkpoints]
num_checkpoints_passed = 0

simulation_paused = configs['debug']['start paused']

while True:
    clock.tick(60)

    keys = pg.key.get_pressed()

    for event in pg.event.get():
        # Close the window when the X is clicked
        if event.type == pg.QUIT:
            pg.quit()
            quit()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                simulation_paused = False if simulation_paused else True
            elif event.key == pg.K_s:
                configs['debug']['show start point'] = False if configs['debug']['show start point'] else True
            elif event.key == pg.K_c:
                configs['debug']['show checkpoints'] = False if configs['debug']['show checkpoints'] else True
            elif event.key == pg.K_v:
                configs['debug']['show vectors'] = False if configs['debug']['show vectors'] else True
            elif event.key == pg.K_h:
                configs['debug']['highlight colliding'] = False if configs['debug']['highlight colliding'] else True

    if not simulation_paused:
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


    # Display everything
    window.fill(configs['display']['background color'])
    track.display(configs['debug']['highlight colliding'], configs['debug']['show checkpoints'], configs['debug']['show start point'])
    car.display(ticks_passed, configs['debug']['show vectors'], configs['debug']['highlight colliding'])
    if simulation_paused:
        sub_surf = pg.font.Font.render(font, 'Simulation paused.', True, '#ff0000')
        window.blit(sub_surf, (7, 7))
    pg.display.flip()

    if not simulation_paused:
        ticks_passed += 1