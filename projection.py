import sys, pygame, engine, math, time

pygame.init()
screen = pygame.display.set_mode((1280, 720), 0, 32)

xoff = 500
yoff = 500

a = (xoff + -100, yoff + -100)
b = (xoff +  100, yoff + -100)
c = (xoff +  100, yoff + 100)
d = (xoff + -100, yoff + 100)

while True:

    screen.fill((200, 200, 200))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                sys.exit(0)

    pygame.draw.polygon(screen, (0, 255, 255), (a, b, c, d), 0)

    pygame.display.flip()

    time.sleep(1 / 60)

