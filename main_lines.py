import sys, pygame
from engine.display import Display
from engine.event_listener import EventListener

display = Display(640, 480)
listener = EventListener()

while 1:
    listener.update()

    display.draw()