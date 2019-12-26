import sys, pygame
pygame.init()

size = width, height = 320, 240
speed = [2, 2]
black = 0, 0, 0
red = 1, 0, 0

screen = pygame.display.set_mode(size)

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    screen.fill(black)
    pygame.draw.line(screen, red, [10, 10], [20, 20], 3)
    pygame.display.flip()

