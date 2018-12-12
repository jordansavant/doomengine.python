import pygame

class Display(object):
    def __init__(self, resW, resH):
        self.width = resW
        self.height = resH
        self.size = self.width, self.height
        self.bg = 0, 0, 0
        pygame.init()
        self.screen = pygame.display.set_mode(self.size)
    
    def start(self):
        self.screen.fill(self.bg)
    
    def end(self):
        pygame.display.flip()

    def drawLine(self, line, color, width):
        # line(Surface, color, start_pos, end_pos, width=1) -> Rect
        pygame.draw.line(self.screen, color, line[0], line[1], width)

    def drawLines(self, lines, color, width):
        # lines(Surface, color, closed, pointlist, width=1) -> Rect
        pygame.draw.line(self.screen, color, False, lines, width)
