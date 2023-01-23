import pygame as pg
from car import *

# Create a window
pg.init()
window = pg.display.set_mode((1080, 720))
pg.display.init()

# Limits framerate/simulation speed to reasonable values
clock = pg.time.Clock()
ticks_passed = 0

# Player Car
car = Car(window, 540, 360, 30)

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

    car.move(throttle_input, steering_input)

    # Display everything
    window.fill('#ffffff')
    car.display(ticks_passed)
    pg.display.flip()

    ticks_passed += 1