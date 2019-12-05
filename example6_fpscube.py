import pygame, math, numpy
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *


# https://pythonprogramming.net/coloring-pyopengl-surfaces-python-opengl
# glued to
# https://3dengine.org/Spectator_(PyOpenGL)/

# matrix positions from flattend numpy matrix
#  0,  1,  2,  3
#  4,  5,  6,  7
#  8,  9, 10, 11
# 12, 13, 14, 15

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

vertices= (
    (1, -1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, -1),
    (1, -1, 1),
    (1, 1, 1),
    (-1, -1, 1),
    (-1, 1, 1)
)

# maps how to connected vertices
edges = (
    (0,1),
    (0,3),
    (0,4),
    (2,1),
    (2,3),
    (2,7),
    (6,3),
    (6,4),
    (6,7),
    (5,1),
    (5,4),
    (5,7)
)

# rgb in float 0-1 values
colors = (
    (1,0,0), #r
    (0,1,0), #g
    (0,0,1), #b
    (0,1,0), #g
    (1,1,1), #wh
    (0,1,1), #cy
    (1,0,0), #r
    (0,1,0), #g
    (0,0,1), #b
    (1,0,0), #r
    (1,1,1), #wh
    (0,1,1), #cy
)

# surfaces are groups of vertices
# indexes to the vertices list
surfaces = (
    (0,1,2,3),
    (3,2,7,6),
    (6,7,5,4),
    (4,5,1,0),
    (1,5,7,2),
    (4,0,3,6)
)

def Cube():

    # render colored surfaces as quads
    glBegin(GL_QUADS)
    for surface in surfaces:
        x = 0
        for vertex in surface:
            x+=1
            glColor3fv(colors[x])
            glVertex3fv(vertices[vertex])
    glEnd()

    # render lines between vertices
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()


listener = EventListener()
moveSpeed = .2
lookSpeed = .2
def on_a():
    strafe = moveSpeed
    m = glGetDoublev(GL_MODELVIEW_MATRIX).flatten()
    glTranslate(strafe*m[0],strafe*m[4],strafe*m[8])
listener.onKeyHold(pygame.K_a, on_a)
def on_d():
    strafe = -moveSpeed
    m = glGetDoublev(GL_MODELVIEW_MATRIX).flatten()
    glTranslate(strafe*m[0],strafe*m[4],strafe*m[8])
listener.onKeyHold(pygame.K_d, on_d)
def on_w():
    fwd = moveSpeed
    m = glGetDoublev(GL_MODELVIEW_MATRIX).flatten()
    glTranslate(fwd*m[2],fwd*m[6],fwd*m[10])
listener.onKeyHold(pygame.K_w, on_w)
def on_s():
    fwd = -moveSpeed
    m = glGetDoublev(GL_MODELVIEW_MATRIX).flatten()
    glTranslate(fwd*m[2],fwd*m[6],fwd*m[10])
listener.onKeyHold(pygame.K_s, on_s)

pitch = 0
pitchMax = math.pi/2 - .05 # maximum rotation negative and positive for pitch
def on_mousemove(deltaX, deltaY, mouseX, mouseY):
    global pitch
    bufer = glGetDoublev(GL_MODELVIEW_MATRIX)
    c = (-1 * numpy.mat(bufer[:3,:3]) * \
        numpy.mat(bufer[3,:3]).T).reshape(3,1)
    # c is camera center in absolute coordinates,
    # we need to move it back to (0,0,0)
    # before rotating the camera
    glTranslate(c[0],c[1],c[2])
    m = bufer.flatten()

    # yaw in y axis unlimited
    glRotate(deltaX * lookSpeed, m[1], m[5], m[9])

    # pitch in x axis should be limited to -90 and +90 degrees
    pitchdeltaDegrees = deltaY * lookSpeed
    pitchdeltaRadians = pitchdeltaDegrees * math.pi / 180
    newPitch = pitch + pitchdeltaRadians
    if newPitch < pitchMax and newPitch > -pitchMax:
        pitch = newPitch
        glRotate(pitchdeltaDegrees, m[0], m[4], m[8])

    # compensate roll (not sure what this does yet)
    glRotated(-math.atan2(-m[4],m[5]) * \
        57.295779513082320876798154814105 ,m[2],m[6],m[10])
    # reset translation back to where we were
    glTranslate(-c[0],-c[1],-c[2])

listener.onMouseMove(on_mousemove)

def main():

    pygame.init()
    display = (1280, 720)
    # DOUBLEBUF is a type of buffering where there are
    # two buffers to comply with monitor refresh rates
    # OPENGL says we will be doing opengl calls
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    # Make mouse virtual input so we can get relativeX
    # and Y better for fps
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    # fov, aspect ratio, nearz, farz clipping planes
    # "nearz and farz values are supposed to be positive
    #  because they are in relation to your perspective,
    #  not in relation to your actual location within the
    #  3D environment."
    glMatrixMode(GL_PROJECTION)
    gluPerspective(75, (display[0] / display[1]), 0.1, 500.0)

    glMatrixMode(GL_MODELVIEW)
    # move perspective by x, y, z (-5 to be back from cube)
    glTranslatef(0.0, 0.0, -5.0)

    # game loop
    while True:

        # listen to input and update camera matrices
        listener.update()

        # clear buffers
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        # render cube lines
        Cube()

        # update display
        pygame.display.flip()

        # update loop sleep 60fpsish
        pygame.time.wait(16)

main()

