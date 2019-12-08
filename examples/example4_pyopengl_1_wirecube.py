import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# https://pythonprogramming.net/opengl-rotating-cube-example-pyopengl-tutorial/

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

def Cube():
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def main():
    pygame.init()
    display = (1280, 720)
    # DOUBLEBUF is a type of buffering where there are
    # two buffers to comply with monitor refresh rates
    # OPENGL says we will be doing opengl calls
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    # fov, aspect ratio, nearz, farz clipping planes
    # "nearz and farz values are supposed to be positive
    #  because they are in relation to your perspective,
    #  not in relation to your actual location within the
    #  3D environment."
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)

    # move perspective by x, y, z (-5 to be back from cube)
    glTranslatef(0.0,0.0, -5)

    # game loop
    while True:
        # pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()

        # rotate current matrix by, x,y,z (w?) (radians?)
        glRotatef(1, 3, 1, 1)
        # clear buffers
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        # render cube lines
        Cube()
        # update display
        pygame.display.flip()
        # update loop sleep
        pygame.time.wait(10)

main()

