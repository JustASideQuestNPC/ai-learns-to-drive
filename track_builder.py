import pygame as pg
import json

def multi_line_text(window, font, font_size, lines, start_coords = (5, 5)) -> None:
    for i, line in enumerate(lines):
        sub_surf = font.render(line, True, '#000000')
        window.blit(sub_surf, (start_coords[0], start_coords[1] + i * 18))

# Create a window
pg.init()
window = pg.display.set_mode((1080, 720))
pg.display.init()

# Used for displaying builder states and other info onscreen
display_font = pg.font.SysFont('monospace', 14)
display_text = 'waiting...'

# Limits framerates to a reasonable value
clock = pg.time.Clock()

# Builder data
border_points = []
finished_border_points = []
start_point = ()
current_checkpoint = []
all_checkpoints = []
border_data = []

# Possible states:
#   0: Placing 1st border
#   1: Placing 2nd border
#   3: Placing start point
#   4: Placing checkpoints
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
            # When placing the start point, place the start point and go to the next stage (checkpoints)
            elif builder_state == 2:
                start_point = mouse_pos
                builder_state += 1
            # When placing checkpoints:
            elif builder_state == 3:
                # Add checkpoints if the left button is pressed...
                if event.button == 1:
                    current_checkpoint.append(mouse_pos)
                    if len(current_checkpoint) >= 2:
                        all_checkpoints.append(current_checkpoint)
                        current_checkpoint = []
                # ...and remove them if the right button is pressed
                elif event.button == 3 and len(all_checkpoints) > 0:
                    all_checkpoints.pop(-1)

        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN:
                if builder_state == 0 and len(border_points) >= 3:
                    finished_border_points = border_points
                    border_data = [(border_points[i-1], border_points[i]) for i in range(len(border_points))]
                    border_points = []
                    builder_state += 1
                elif builder_state == 1 and len(border_points) >= 3:
                    appended_data = [(border_points[i-1], border_points[i]) for i in range(len(border_points))]
                    border_data += appended_data
                    builder_state += 1
                elif builder_state == 2:
                    pass # Do nothing, state 2 is placing the start point and only advances on click
                elif builder_state == 3 and len(all_checkpoints) >= 3:
                    # Construct the dictionary for the track
                    track_data = {}
                    track_data['borders'] = border_data
                    track_data['start point'] = start_point
                    track_data['checkpoints'] = all_checkpoints
                    # Get existing data from the tracks file
                    with open('tracks.json', 'r') as tracks_file:
                        existing_data = json.load(tracks_file)
                    existing_data.append(track_data)
                    
                    # Write new data to the tracks file
                    with open('tracks.json', 'w') as tracks_file:
                        json.dump(existing_data, tracks_file, indent=2)
                    pg.quit()
                    quit()

    # Display everything
    window.fill('#ffffff')

    # Handles some edge cases at the beginning of the process
    if builder_state == 0 or builder_state == 1:
        if len(border_points) == 0:
            pg.draw.line(window, '#000000', mouse_pos, mouse_pos, 4)
        elif len(border_points) == 1:
            pg.draw.line(window, '#000000', border_points[0], mouse_pos, 4)
        else:
            displayed_border = border_points + [mouse_pos]
            pg.draw.lines(window, '#000000', True, displayed_border, 4)
    else:
        pg.draw.lines(window, '#a0a0a0', True, border_points, 4)
    
    # Draws finished borders in grey
    if len(finished_border_points) > 0:
        pg.draw.lines(window, '#a0a0a0', True, finished_border_points, 4)

    if builder_state == 2:
        pg.draw.circle(window, '#00ff00', mouse_pos, 5)
    elif builder_state > 2:
        pg.draw.circle(window, '#50ff50', start_point, 5)

    if builder_state == 3:
        if len(current_checkpoint) == 0:
            pg.draw.line(window, '#ff0000', mouse_pos, mouse_pos, 2)
        elif len(current_checkpoint) == 1:
            pg.draw.line(window, '#ff0000', current_checkpoint[0], mouse_pos, 2)
        for cp in all_checkpoints:
            pg.draw.line(window, '#ff5050', cp[0], cp[1], 2)

    # Display some info text in the corner of the screen
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
    elif builder_state == 3:
        display_text = ['Placing checkpoints...more is always better!',
                        'Left click to place checkpoints, and right click to remove your last checkpoint.',
                        'Press enter to finish and save your track.']

    multi_line_text(window, display_font, 16, display_text)
    pg.display.flip()