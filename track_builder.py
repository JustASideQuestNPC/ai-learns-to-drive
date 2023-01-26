import pygame as pg
import shapely
import json

# Create a window
pg.init()
window = pg.display.set_mode((1080, 720))
pg.display.init()

# Limits framerates to a reasonable value
clock = pg.time.Clock()

borders = []

while True:
    clock.tick(60)
    for event in pg.event.get():
        # Close the window if the X is clicked
        if event.type == pg.QUIT:
            pg.quit()
            quit()

    # Display everything
    window.fill('#ffffff')

    pg.display.flip()