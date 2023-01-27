import PySimpleGUI as sg
import json

# Load existing configs
with open('configs.json', 'r') as config_file:
    configs = json.load(config_file)

layout = [[sg.Text('hi there')]]

window = sg.Window('Simulation Configurator', layout)

# Event loop
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break

window.close()