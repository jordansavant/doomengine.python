import pygame

class Display(object):
    def __init__(self, resW, resH):
        self.width = resW
        self.height = resH
        self.size = self.width, self.height
        self.bg = 0, 0, 0
        self.scale = 1.0
        self.offset = [0, 0]
        self.fullscreen = False
        pygame.init()
        self.screen = pygame.display.set_mode(self.size)
    
    def start(self):
        self.screen.fill(self.bg)
    
    def end(self):
        pygame.display.flip()

    def toggleFullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode(self.size, pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(self.size)

    def drawLine(self, line, color, width):
        # line(Surface, color, start_pos, end_pos, width=1) -> Rect
        pygame.draw.line(self.screen, color, [line[0][0] * self.scale, line[0][1] * self.scale], [line[1][0] * self.scale, line[1][1] * self.scale], width)

    def drawLines(self, lines, color, width, connect = False):
        scaledLines = []
        if self.scale != 1:
            for point in lines:
                scaledLines.append([point[0] * self.scale, point[1] * self.scale])
            pygame.draw.lines(self.screen, color, connect, scaledLines, width)
        else:
            pygame.draw.lines(self.screen, color, connect, lines, width)

    def drawPolygon(self, points, color, width):
        pygame.draw.polygon(self.screen, color, points, width)


    def drawPoint(self, pos, color, width):
        pygame.draw.circle(self.screen, color, [(int)(pos[0] * self.scale), (int)(pos[1] * self.scale)], width)
    
    def drawText(self, text, textpos):
        self.screen.blit(text, textpos)
