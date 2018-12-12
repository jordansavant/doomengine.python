import sys, pygame

class EventListener(object):
    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    sys.exit(0)
