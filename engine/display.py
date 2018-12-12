import pygame

class Display(object):
    def __init__(self, resW, resH):
        self.width = resW
        self.height = resH
        self.size = self.width, self.height
        self.bg = 0, 0, 0
        pygame.init()
        self.screen = pygame.display.set_mode(self.size)
    
    def draw(self):
        self.screen.fill(self.bg)
        pygame.display.flip()
