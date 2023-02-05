import json
import PySimpleGUI as sg
from math import floor
sg.theme('Dark Blue 3')

# Load existing configs
with open('configs.json', 'r') as config_file:
    configs = json.load(config_file)


def toggle(x) -> bool:
    return False if x == True else True

# range(), but it works with fractional steps
def frange(start, stop, step) -> list:
    reciprocal = 1 / step
    int_range = (stop - start) / step
    return [i / reciprocal for i in range(start, int(int_range) + start)]

def save_configs():
    pass

config_displays = [
    'Yes' if configs['debug']['show vectors'] else 'No',
    'Yes' if configs['debug']['highlight colliding'] else 'No',
    'Yes' if configs['debug']['show checkpoints'] else 'No',
    'Yes' if configs['debug']['show start point'] else 'No',
    'Yes' if configs['debug']['show raycasts'] else 'No',
    'Yes' if configs['training']['allow braking'] else 'No',
    'Yes' if configs['training']['allow partial inputs'] else 'No',
]

debug_tab = [
        [sg.Text('Display vectors:'), sg.Button(config_displays[0], key='-DISPLAY_VECTORS-')],
        [sg.Text('Highlight collisions:'), sg.Button(config_displays[1], key='-HIGHLIGHT_COLLISIONS-')],
        [sg.Text('Show checkpoints:'), sg.Button(config_displays[2], key='-SHOW_CHECKPOINTS-')],
        [sg.Text('Show starting point:'), sg.Button(config_displays[3], key='-SHOW_START_POINT-')],
        [sg.Text('Show raycasts:'), sg.Button(config_displays[4], key='-SHOW_RAYCASTS-')],
        [sg.Text('Start with simulation paused:'), sg.Button(config_displays[4], key='-START_PAUSED-')]]

car_tab = [
        [sg.Text('Top speed:'), sg.Spin([i for i in range(1, 100)], initial_value=configs['car']['top speed'], key='-TOP_SPEED-', size=5)],
        [sg.Text('Acceleration:'), sg.Spin([i for i in frange(0, 10, 0.1)], initial_value=configs['car']['acceleration'], key='-ACCELERATION-', size=5)],
        [sg.Text('Braking force:'), sg.Spin([i for i in frange(0, 10, 0.1)], initial_value=configs['car']['braking force'], key='-BRAKING_FORCE-', size=5)],
        [sg.Text('Steering response:'), sg.Spin([i for i in range(0, 180)], initial_value=configs['car']['steering response'], key='-STEERING_RESPONSE-', size=5)],
        [sg.Text('Ground Friction:'), sg.Spin([i for i in frange(0, 10, 0.005)], initial_value=configs['car']['base deceleration'], key='-GROUND_FRICTION-', size=5)],
        [sg.Text('Grip percentage:'), sg.Spin([i for i in range(0, 100)], initial_value=int(configs['car']['base grip'] * 100), key='-GRIP_PERCENTAGE-', size=5)],
        [sg.Text('Simulation speed (ticks/sec):'), sg.Spin([i for i in range(1, 1200)], initial_value=configs['training']['simulation speed'], key='-SIMULATION_SPEED-', size=5)]
]

training_tab = [
        [sg.Text('Allow AI to brake:'), sg.Button(config_displays[5], key='-ALLOW_BRAKING-')],
        [sg.Text('Allow partial inputs:'), sg.Button(config_displays[6], key='-ALLOW_PARTIAL_INPUTS-')],
        [sg.Text('Passive survival bonus:'), sg.Spin([i for i in range(-50, 50)], initial_value=configs['training']['survival bonus'], key='-SURVIVAL_BONUS-', size=5)],
        [sg.Text('Death penalty'), sg.Spin([i for i in range(-50, 50)], initial_value=configs['training']['death penalty'], key='-DEATH_PENALTY-', size=5)],
        [sg.Text('Checkpoint bonus:'), sg.Spin([i for i in range(-50, 50)], initial_value=configs['training']['checkpoint bonus'], key='-CHECKPOINT_BONUS-', size=5)],
        [sg.Text('Checkpoint speed multiplier:'), sg.Spin([i for i in range(0, 10)], initial_value=configs['training']['checkpoint speed multiplier'], key='-CHECKPOINT_SPEED_MULTIPLIER-', size=5)],
]

layout = [[sg.TabGroup([
        [sg.Tab('Car', car_tab), sg.Tab('Training', training_tab), sg.Tab('Debug', debug_tab)],])],
        [sg.Button('Save'), sg.Button('Quit')]
]

window = sg.Window('Simulation Configurator', layout)

# Event loop
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Quit':
        break
    elif event == '-DISPLAY_VECTORS-':
        configs['debug']['show vectors'] = toggle(configs['debug']['show vectors'])
        window['-DISPLAY_VECTORS-'].update('Yes' if configs['debug']['show vectors'] else 'No')
    elif event == '-HIGHLIGHT_COLLISIONS-':
        configs['debug']['highlight colliding'] = toggle(configs['debug']['highlight colliding'])
        window['-HIGHLIGHT_COLLISIONS-'].update('Yes' if configs['debug']['highlight colliding'] else 'No')
    elif event == '-SHOW_CHECKPOINTS-':
        configs['debug']['show checkpoints'] = toggle(configs['debug']['show checkpoints'])
        window['-SHOW_CHECKPOINTS-'].update('Yes' if configs['debug']['show checkpoints'] else 'No')
    elif event == '-SHOW_START_POINT-':
        configs['debug']['show start point'] = toggle(configs['debug']['show start point'])
        window['-SHOW_START_POINT-'].update('Yes' if configs['debug']['show start point'] else 'No')
    elif event == '-SHOW_RAYCASTS-':
        configs['debug']['show raycasts'] = toggle(configs['debug']['show raycasts'])
        window['-SHOW_RAYCASTS-'].update('Yes' if configs['debug']['show raycasts'] else 'No')
    elif event == '-ALLOW_BRAKING-':
        configs['training']['allow braking'] = toggle(configs['training']['allow braking'])
        window['-ALLOW_BRAKING-'].update('Yes' if configs['training']['allow braking'] else 'No')
    elif event == '-ALLOW_PARTIAL_INPUTS-':
        configs['training']['allow partial inputs'] = toggle(configs['training']['allow partial inputs'])
        window['-ALLOW_PARTIAL_INPUTS-'].update('Yes' if configs['training']['allow partial inputs'] else 'No')
    elif event == '-START_PAUSED-':
        configs['debug']['start paused'] = toggle(configs['debug']['start paused'])
        window['-START_PAUSED-'].update('Yes' if configs['debug']['start paused'] else 'No')
    elif event == 'Save':
        configs['car']['top speed'] = window['-TOP_SPEED-'].Get()
        configs['car']['acceleration'] = window['-ACCELERATION-'].Get()
        configs['car']['braking force'] = window['-BRAKING_FORCE-'].Get()
        configs['car']['steering response'] = window['-STEERING_RESPONSE-'].Get()
        configs['car']['base deceleration'] = window['-GROUND_FRICTION-'].Get()
        configs['car']['base grip'] = window['-GRIP_PERCENTAGE-'].Get() / 100
        configs['training']['simulation speed'] = window['-SIMULATION_SPEED-'].Get()
        configs['training']['survival bonus'] = window['-SURVIVAL_BONUS-'].Get()
        configs['training']['death penalty'] = window['-DEATH_PENALTY-'].Get()
        configs['training']['checkpoint bonus'] = window['-CHECKPOINT_BONUS-'].Get()
        configs['training']['checkpoint speed multiplier'] = window['-CHECKPOINT_SPEED_MULTIPLIER-'].Get()

        with open('configs.json', 'w') as config_file:
            json.dump(configs, config_file, indent=2)

window.close()