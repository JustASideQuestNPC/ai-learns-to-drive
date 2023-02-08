# AI Learns to Drive
Oh wow, you actually clicked the link! This is a set of programs I wrote over about a week and a half to train an AI to play a small driving simulation, and I figured I might as well let other people play with it too, because that way no one has to suffer like I did. It should be pretty easy to use, but I'm still going to write detailed instructions, because I live in a country where toasters have stickers telling you not to take the in the bath with you.

# Setup
If you already have python set up on your computer, you can skip this section and go down to "Packages". If you don't, read this section first.

## Python (not the snake)
Since this code is written entirely in Python, you do, in fact, need to have Python on your computer to run it (shocker, I know). If you don't already have it, the first thing you'll need is a code editor (unless you feel like doing everything in Microsoft Word). I recommend [Visual Studio Code](https://code.visualstudio.com/), but there are also some other good ones (All the instructions here are for VSCode, though). The next thing you'll need is [Python](https://www.python.org/downloads/), and then you'll need to get the Python extension for VSCode (Just open the Extensions tab and search for it. It's the one by Microsoft). You can add this project into VSCode by just clicking the "Clone Git Repository" button and pasting the link to this repo into the box.

## Packages (not from FedEx)
What, did you think that was it? This is programming, so if something's this easy it probably means it won't work. Before you can use any of this, you'll need to get some packages that have all the external libraries this monstrosity uses. If you're new to packages you can just open a terminal in VSCode and use `pip install <name>`, assuming everything is installed right. You'll need four different packages:
- Pygame (`pip install pygame`) - this is technically for making games, but it also makes graphics really easy.
- Shapely (`pip install shapely`) - most of this one is for geometry and linear algebra and other things that are too intense for my three brain cells. All I know is that it can tell me when two lines cross, which makes it really good for collisions.
- NEAT (`pip install neat-python`) - this handles everything involving the AIs, which are much smarter than me - the neural networks can equal a whole *five* brain cells!
- PYSimpleGui (`pip install pysimplegui`) - this one is only used in the configurator program. You can skip installing it, but then you'll have to edit `configs.json` directly (not that there's anything wrong with that).

# How to ~~Appease the Overlords~~ Use this Program
1. Open `ai_played.py`.
2. Click the run button.
3. Watch the AI learn to drive.

Okay, *fine*, there's a bit more than that. You can run `track_builder.py` to build your own tracks for the AI to drive on (it'll walk you through the process), and you can also run `human_played.py` to drive the car yourself (use arrow keys/WASD).

When the simulation is running, there's a few hotkeys you can press to do things:
- Spacebar will pause/unpause the simulation
- V will display the velocity vectors of each car
- C will display every checkpoint on the track
- S will display the start point where each car spauwns on the track
- H will change the colors of cars, checkpoints, and walls whenever they're colliding with something
- R will show the raycasts, which are how the AIs "see" the track (this doesn't work in the human-played simulation)

You can also run `configurator.py` to modify a ton of things involving physics and AI training. Most of the configs are self-explanatory, but there's still a few that might be a little confusing:
- "Steering response" is how many degrees the car rotates per tick when at full steering input.
- "Ground friction" is how quickly the car decelerates when it's not accelerating or braking.
- "Grip percentage" controls how much the car drifts while turning. At 100% grip, the car will never drift at all, and at 0 percent, it will spin around without ever moving in a different direction.
- "Allow AI to brake" is self-explanatory, but I recommend keeping it disabled. Having it enabled makes training *much* slower and doesn't make the AI much better at driving.
- "Allow partial inputs" determines whether the AI can only use the maximum possible steering/throttle inputs, or if it can use inputs that are less intense. I recommend keeping it disabled for the same reasons as "Allow AI to brake".
- "Passive survival bonus" is how much an AI's fitness is increased just for staying alive another tick. Setting this to anything above 0 will probably train your AIs to just not move at all, but making it negative may have interesting results.
- "Checkpoint speed multiplier" increases how much fitness an AI gets from passing through a checkpoint based on how fast its car is moving when it crosses the line. If the car is stopped, the checkpoint bonus isn't multiplied at all, and if the car is at its top speed, the bonus is multiplied by the full speed multiplier.
- "Minimum safe speed" and "Slow AI kill timer" are used to kill AIs that just stand still. AIs that spend longer than the timer moving slower than the minimum safe speed are destroyed (the timer is reset once the AI moves at a safe speed for at least one tick).