import pygame, engine_ocl, math, time
from engine.display import Display
from engine.eventlistener import EventListener

display = Display(1920, 1080)
listener = EventListener()
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)
font = pygame.font.Font(None, 36)

while True:
    listener.update()

    display.start()

    display.drawLine([[10, 10], [20, 20]], (255, 255, 255), 1)

    display.end()

    time.sleep(1 / 60)
