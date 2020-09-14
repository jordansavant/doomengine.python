import sys, pygame

class EventListener(object):
    def __init__(self):
        self.keyUpCallbacks = {}
        self.keyDownCallbacks = {}
        self.keyHoldCallbacks = {}
        self.mouseMoveCallbacks = []
        self.keyHolds = {}

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                self.keyHolds[event.key] = True
                if event.key in self.keyDownCallbacks:
                    for callback in self.keyDownCallbacks[event.key]:
                        callback()
            if event.type == pygame.KEYUP:
                self.keyHolds[event.key] = False
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()
                if event.key in self.keyUpCallbacks:
                    for callback in self.keyUpCallbacks[event.key]:
                        callback()
            if event.type == pygame.MOUSEMOTION:
                for callback in self.mouseMoveCallbacks:
                    mouseX, mouseY = pygame.mouse.get_pos()
                    mouserelX, mouserelY = pygame.mouse.get_rel()
                    callback(mouserelX, mouserelY, mouseX, mouseY)
        for k, v in self.keyHolds.items():
            if v:
                if k in self.keyHoldCallbacks:
                    for callback in self.keyHoldCallbacks[k]:
                        callback()


    def register(self, callbacks, key, func):
        if key not in callbacks:
            callbacks[key] = []
        callbacks[key].append(func)

    def onKeyUp(self, key, func):
        self.register(self.keyUpCallbacks, key, func)

    def onKeyDown(self, key, func):
        self.register(self.keyDownCallbacks, key, func)

    def onKeyHold(self, key, func):
        self.register(self.keyHoldCallbacks, key, func)

    def onMouseMove(self, func):
        self.mouseMoveCallbacks.append(func)
