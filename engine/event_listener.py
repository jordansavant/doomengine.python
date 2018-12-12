import sys, pygame

class EventListener(object):

    def __init__(self):
        self.keyUpCallbacks = {}

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    sys.exit(0)
                if event.key in self.keyUpCallbacks:
                    for callback in self.keyUpCallbacks[event.key]:
                        callback()

    def onKeyUp(self, key, func):
        if key not in self.keyUpCallbacks:
            self.keyUpCallbacks[key] = []
        self.keyUpCallbacks[key].append(func)