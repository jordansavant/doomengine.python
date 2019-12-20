import pygame, os, math
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

class Game2D(object):

    def __init__(self):
        self.over = False
        self.fps = 60
        self.keyUpCallbacks = {}
        self.keyDownCallbacks = {}
        self.keyHoldCallbacks = {}
        self.mouseMoveCallbacks = []
        self.keyHolds = {}

    def setupWindow(self, width, height):
        self.width = width
        self.height = height
        pygame.init()
        os.environ['SDL_VIDEO_CENTERED'] = '1' # center window on screen
        screen = pygame.display.set_mode((width, height), DOUBLEBUF|OPENGL) # build window with opengl
        glEnable(GL_BLEND); # allows for alpha transparency on color
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

    def events(self):
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

    def setFPS(self, fps):
        self.fps = fps

    def sleep(self, ms=None):
        if ms is None:
            ms = (int)(1000 / self.fps)
        pygame.time.wait(ms) # dinky 60fps

    def drawStart(self):
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
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

    def drawPoint(self, pos, rgba, radius):
        glColor4f(rgba[0], rgba[1], rgba[2], rgba[3])
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(pos[0], pos[1]);
        for angle in range(10, 3610, 2):
            angle = angle / 10 # convert back down to degrees
            x2 = pos[0] + math.sin(angle) * radius;
            y2 = pos[1] + math.cos(angle) * radius;
            glVertex2f(x2, y2);
        glEnd()

    def drawRectangle(self, pos, width, height, rgba):
        glColor4f(rgba[0], rgba[1], rgba[2], rgba[3])
        glBegin(GL_QUADS)
        glVertex2f(pos[0], pos[1])
        glVertex2f(pos[0] + width, pos[1])
        glVertex2f(pos[0] + width, pos[1] + height)
        glVertex2f(pos[0], pos[1] + height)
        glEnd()

    def drawBox(self, tl, tr, br, bl, rgba, width):
        self.drawLine(tl, tr, rgba, width)
        self.drawLine(tr, br, rgba, width)
        self.drawLine(br, bl, rgba, width)
        self.drawLine(bl, tl, rgba, width)
