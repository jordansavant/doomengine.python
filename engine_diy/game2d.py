import pygame, os
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

class Game2D(object):

    def __init__(self):
        self.over = False

    def setupWindow(self, width, height):
        self.width = width
        self.height = height
        pygame.init()
        os.environ['SDL_VIDEO_CENTERED'] = '1' # center window on screen
        screen = pygame.display.set_mode((width, height), DOUBLEBUF|OPENGL) # build window with opengl

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.over = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    self.over = True

    def sleep(self):
        pygame.time.wait(16) # dinky 60fps

    def drawStart(self):
        glPushMatrix()
        # projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0.0, self.width, self.height, 0.0)
        # models
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def drawEnd(self):
        glPopMatrix()
        pygame.display.flip() # buffer swap

    def drawLine(self, start, end, rgba, width):
        glLineWidth(width)
        glColor4f(rgba[0], rgba[1], rgba[2], rgba[3])
        glBegin(GL_LINES)
        glVertex2f(start[0], start[1])
        glVertex2f(end[0], end[1])
        glEnd()

