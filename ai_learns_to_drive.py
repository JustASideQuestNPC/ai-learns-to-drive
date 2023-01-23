import pygame as pg

# Create a window
pg.init()
window = pg.display.set_mode((1080, 720))
pg.display.init()

while True:
    for event in pg.event.get():
        # Close the window when the X is clicked
        if event.type == pg.QUIT:
            pg.quit()
            quit()
    
    # Display everything
    window.fill('#FFFFFF')

    pg.display.flip()