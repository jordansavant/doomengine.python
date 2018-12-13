import pygame, bsp
from engine.display import Display
from engine.event_listener import EventListener


display = Display(640, 480)
listener = EventListener()

# Lines
lines = [
    [[50, 50], [100, 100]],
    [[400, 400], [400, 90]],
    [[160, 325], [350, 220]]
]

# render mode ops
mode = 0
max_modes = 3
def mode_swap():
    global mode
    mode = (mode + 1) % max_modes
    print(mode)

# register callback function for changing the render mode
listener.onKeyUp(pygame.K_RETURN, mode_swap)

bsp = bsp.BSP(lines)

while True:
    listener.update()

    display.start()

    if mode == 0:
        for line in lines:
            display.drawLine(line, (0, 0, 255), 5)
    elif mode == 1:
        for line in lines:
            display.drawLine(line, (255, 0, 255), 5)

    display.end()