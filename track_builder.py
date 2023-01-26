import pygame as pg
import json

def multi_line_text(window, font, font_size, lines, start_coords = (5, 5)) -> None:
    for i, line in enumerate(lines):
        sub_surf = font.render(line, True, '#000000')
        window.blit(sub_surf, (start_coords[0], start_coords[1] + i * 20))

# Create a window
pg.init()
window = pg.display.set_mode((1080, 720))
pg.display.init()

# Used for displaying builder states and other info onscreen
display_font = pg.font.SysFont('monospace', 16)
display_text = 'waiting...'

# Limits framerates to a reasonable value
clock = pg.time.Clock()

# Single points for track borders, used for display and building
border_points = []
finished_border_points = []

# Possible states:
#   0: Placing 1st border
#   1: Placing 2nd border
#   3: Placing checkpoints
#   4: Placing start point
builder_state = 0
while True:
    clock.tick(60)

    mouse_pos = pg.mouse.get_pos()

    for event in pg.event.get():
        # Close the window if the X is clicked
        if event.type == pg.QUIT:
            pg.quit()
            quit()

        # Clicking the mouse does many things based on the state of the builder
        elif event.type == pg.MOUSEBUTTONDOWN:
            # When constructing the borders of the track:
            if builder_state == 0 or builder_state == 1:
                # Add a point if the left button is pressed...
                if event.button == 1:
                    border_points.append(mouse_pos)
                # ...and remove one if the right button is pressed
                elif event.button == 3 and len(border_points) > 0:
                    border_points.pop(-1)

        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN:
                if builder_state == 0 and len(border_points) >= 3:
                    finished_border_points = border_points
                    border_points = []
                    builder_state += 1
                elif builder_state == 1 and len(border_points) >= 3:
                    builder_state += 1
                elif builder_state == 2:
                    pass # Do nothing, state 2 is placing the start point and advances on click

    # Display everything
    window.fill('#ffffff')

    # Handles some edge cases at the beginning of the process
    if builder_state == 0 or builder_state == 1:
        if len(border_points) == 0:
            pg.draw.line(window, '#000000', mouse_pos, mouse_pos, 2)
        elif len(border_points) == 1:
            pg.draw.line(window, '#000000', border_points[0], mouse_pos, 2)
        else:
            displayed_border = border_points + [mouse_pos]
            pg.draw.lines(window, '#000000', True, displayed_border, 2)
    else:
        pg.draw.lines(window, '#a0a0a0', True, border_points, 2)
    
    if len(finished_border_points) > 0:
        pg.draw.lines(window, '#a0a0a0', True, finished_border_points, 2)

    if builder_state == 0:
        display_text = ['Placing first border...DO NOT let borders intersect!',
                        'Left click to place a point, right click to remove points.',
                        'Press Enter to finish and go to the next step.']
    elif builder_state == 1:
        display_text = ['Placing second border...DO NOT let borders intersect!',
                        'Left click to place a point, right click to remove points.',
                        'Press Enter to finish and go to the next step.']
    elif builder_state == 2:
        display_text = ['Placing start point...make sure it\'s inside the track!',
                        'Left click to place the starting point and move on to the next step.']

    multi_line_text(window, display_font, 16, display_text)
    pg.display.flip()