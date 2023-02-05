import pygame as pg
from json import load
from car import Car
from track import Track
from raycaster import Raycaster
from concurrent.futures import ThreadPoolExecutor
from math import sin, cos, radians
import neat
from os import path
from random import choice

population_size = 5

# Load configs
with open('configs.json', 'r') as config_file:
    configs = load(config_file)

# Load tracks
with open('tracks.json', 'r') as tracks_file:
    tracks = load(tracks_file)

# Loops through all the AI cars and computes collisions for all of them
def do_all_collisions(track, cars) -> list:
    collision_data = []
    for car in cars:
        collision_data.append(track.do_collisions(car.hitbox_points))
    return collision_data

# Determines what inputs to give cars based on how training is configured
def determine_control_input(inputs) -> tuple:
    if not configs['training']['allow partial input']:
        if inputs[0] < -0.5 and configs['training']['allow braking']:
            throttle = -1
        elif inputs[0] > 0.5:
            throttle = 1
        else:
            throttle = 0

        if inputs[1] < -0.5:
            steering = -1
        elif inputs[1] > 0.5:
            steering = 1
        else:
            steering = 0
    else:
        if throttle < -1: throttle = -1
        elif throttle > 1: throttle = 1

        if steering < -1: steering = -1
        elif steering > 1: steering = 1

    return (throttle, steering)

# Maps a value from one range of values to the equivalent place in another range of values.
def map_ranges(value, from_min, from_max, to_min, to_max):
    from_span = from_max - from_min
    to_span = to_max - to_min

    scaled = float(value - from_min) / float(from_span)

    return to_min + (scaled * to_span)

# Create a window
pg.init()
window = pg.display.set_mode((1080, 720))
pg.display.init()

font = pg.font.SysFont('monospace', 24)

# Limits framerate/simulation speed to reasonable values
clock = pg.time.Clock()

generation = 1
simulation_paused = configs['debug']['start paused']

# The "fitness function" for the AI, which has them play the simulation and assigns fitness values based on how well they performed
def fitness(genomes, config):
    global generation
    global simulation_paused
    global configs
    max_generation_length = configs['training']['max generation length']

    # Current track
    track = Track(window, choice(tracks))

    # Create the neural networks in the current population
    nets = []
    ge = []
    cars = []
    raycasters = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        cars.append(Car(window, track.start_point, 90))
        raycasters.append(Raycaster(track.start_point, 0))
        g.fitness = 0
        ge.append(g)

    # Used to only count checkpoints once per lap
    passed_checkpoints = [[False for i in track.checkpoints] for c in cars]
    num_checkpoints_passed = [0 for c in cars]

    ticks_passed = 0

    running = True
    while running:
        clock.tick(configs['training']['simulation speed'])

        for event in pg.event.get():
            # Close the window when the X is clicked
            if event.type == pg.QUIT:
                running = False
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
                elif event.key == pg.K_r:
                    configs['debug']['show raycasts'] = False if configs['debug']['show raycasts'] else True

        # Stops training if all AIs are dead
        if len(cars) == 0 or ticks_passed > max_generation_length:
            cars = []
            nets = []
            ge = []
            passed_checkpoints = []
            num_checkpoints_passed = []
            raycasters = []
            ray_distances = []
            collision_results = []
            break
        
        # Do physics and AI calculations if the simulation isn't paused
        if not simulation_paused:
            ray_distances = []
            for i, rc in enumerate(raycasters):
                rc.position = cars[i].position
                rc.angle = -cars[i].facing_angle - 90
                ray_distances.append(rc.cast(track.border_colliders))

            # Do collision and physics calculations in parallel
            with ThreadPoolExecutor() as executor:
                collision_thread = executor.submit(do_all_collisions, track, cars)

                for i, car in enumerate(cars):
                    # Get control input each AI, then move its car
                    throttle_input, steering_input = nets[i].activate(ray_distances[i] + [car.current_speed])

                    car.move(throttle_input, steering_input)

                collision_results = []
                collision_results = collision_thread.result()

                for i, res in enumerate(collision_results):
                    colliding, passed_cp = res

                    if passed_cp != -1 and not passed_checkpoints[i][passed_cp] and not colliding:
                        speed_multiplier = map_ranges(cars[i].current_speed, 0, configs['car']['top speed'],
                                            1, configs['training']['checkpoint speed multiplier'])
                        ge[i].fitness += configs['training']['checkpoint bonus'] * speed_multiplier

                        num_checkpoints_passed[i] += 1
                        passed_checkpoints[i][passed_cp] = True
                        if num_checkpoints_passed[i] == len(passed_checkpoints[i]):
                            num_checkpoints_passed[i] = 0
                            passed_checkpoints[i] = [False for i in track.checkpoints]
                    
                    # Destroy cars if they hit a wall
                    if colliding:
                        ge[i].fitness += configs['training']['death penalty']
                        cars.pop(i)
                        nets.pop(i)
                        ge.pop(i)
                        passed_checkpoints.pop(i)
                        num_checkpoints_passed.pop(i)
                        raycasters.pop(i)
                        ray_distances.pop(i)
                        collision_results.pop(i)
                    else:
                        ge[i].fitness += configs['training']['survival bonus']


        # Display everything
        window.fill(configs['display']['background color'])
        track.display(configs['debug']['highlight colliding'], configs['debug']['show checkpoints'], configs['debug']['show start point'])
        for car in cars:
            car.display(ticks_passed, configs['debug']['show vectors'], configs['debug']['highlight colliding'])

        if configs['debug']['show raycasts']:
            for i, ray in enumerate(ray_distances):
                print(len(ray))
                for a, dist in enumerate(ray):
                    ray_endpoint = (
                        cos(radians(-cars[i].facing_angle - 90 + configs['training']['ray angles'][a])) * dist + cars[i].position[0],
                        sin(radians(-cars[i].facing_angle - 90 + configs['training']['ray angles'][a])) * dist + cars[i].position[1]
                    )
                    pg.draw.line(window, '#00ff00', cars[i].position, ray_endpoint, 2)
                    pg.draw.circle(window, '#707070', ray_endpoint, 5)

        # Display some info on the current generation
        if not simulation_paused:
            info_text = f'Running generation {generation} | {max_generation_length - ticks_passed} ticks until next generation.'
        else:
            info_text = 'Simulation paused.'

        sub_surf = pg.font.Font.render(font, info_text, True, '#ff0000')
        window.blit(sub_surf, (7, 7))

        pg.display.flip()

        # Only advance the tick counter if the simulation isn't paused
        if not simulation_paused:
            ticks_passed += 1

    generation += 1

# Runs the entire program
def run(config_path):
    neat_config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # Creates an AI population
    p = neat.Population(neat_config)

    # Creates reporters that print some updates and statistics on the training to the terminal
    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(neat.StatisticsReporter())

    # Runs the AI for 50 generations
    p.run(fitness, 50)


# Finds the absolute path to the AI config. I have no idea *why* the AI needs the absolute path, but apparently it does.
if __name__ == '__main__':
    local_dir = path.dirname(__file__)
    config_path = path.join(local_dir, 'neat_config.txt')

run(config_path)

pg.quit()
quit()