import pygame, bsp
from engine.display import Display
from engine.event_listener import EventListener
from engine import defs

print("\n\n\n")


display = Display(1280, 720)
listener = EventListener()

# Lines
poly1 = [
    [50, 50], [500, 50], [500, 300], [200, 300]
]

# Line Defs
lineDefs = []
for idx, val in enumerate(poly1):
    lineDef = defs.LineDef()

    # first point, connect to second point
    if idx == 0:
        lineDef.asRoot(poly1[idx][0], poly1[idx][1], poly1[idx + 1][0], poly1[idx + 1][1])
        lineDefs.append(lineDef)

    # some point in the middle
    elif idx < len(poly1) - 1:
        lineDef.asChild(lineDefs[-1], poly1[idx + 1][0], poly1[idx + 1][1])
        lineDefs[-1].nextLineDef = lineDef
        lineDefs.append(lineDef)
    
    # final point, final line, connects back to first point
    elif idx == len(poly1) - 1:
        lineDef.asLeaf(lineDefs[-1], lineDefs[0])
        lineDefs[-1].nextLineDef = lineDef
        lineDefs.append(lineDef)
    

# render mode ops
mode = 0
max_modes = 3
def mode_swap():
    global mode
    mode = (mode + 1) % max_modes
    print(mode)

# register callback function for changing the render mode
listener.onKeyUp(pygame.K_RETURN, mode_swap)

while True:
    listener.update()

    display.start()

    # render the polygons
    if mode == 0:
        for lineDef in lineDefs:
            display.drawLine([lineDef.start, lineDef.end], (0, 0, 255), 2)

    display.end()