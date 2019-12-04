import pygame, math, numpy
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# https://pythonprogramming.net/coloring-pyopengl-surfaces-python-opengl

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



def main():

    pygame.init()
    display = (1280, 720)
    # DOUBLEBUF is a type of buffering where there are
    # two buffers to comply with monitor refresh rates
    # OPENGL says we will be doing opengl calls
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
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

    #glRotatef(25, 2, 1, 0)

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

            # move forward-back or right-left
            # fwd =   .1 if 'w' is pressed;   -0.1 if 's'
            #fwd = .1 * (self.keys[w_key]-self.keys[s_key])
            #strafe = .1 * (self.keys[a_key]-self.keys[d_key])
            #if abs(fwd) or abs(strafe):
                # matrix positions
                #  0,  1,  2,  3
                #  4,  5,  6,  7
                #  8,  9, 10, 11
                # 12, 13, 14, 15
            if event.type == pygame.KEYDOWN:
                # move in X axis
                if event.key == pygame.K_a:
                    strafe = .1
                    m = glGetDoublev(GL_MODELVIEW_MATRIX).flatten()
                    glTranslate(strafe*m[0],strafe*m[4],strafe*m[8])
                if event.key == pygame.K_d:
                    strafe = -.1
                    m = glGetDoublev(GL_MODELVIEW_MATRIX).flatten()
                    glTranslate(strafe*m[0],strafe*m[4],strafe*m[8])

                # move in Z axis
                if event.key == pygame.K_w:
                    fwd = .1
                    m = glGetDoublev(GL_MODELVIEW_MATRIX).flatten()
                    glTranslate(fwd*m[2],fwd*m[6],fwd*m[10])
                if event.key == pygame.K_s:
                    fwd = -.1
                    m = glGetDoublev(GL_MODELVIEW_MATRIX).flatten()
                    glTranslate(fwd*m[2],fwd*m[6],fwd*m[10])

            if event.type == pygame.MOUSEMOTION:
                # get mouse steering
                #mouseX, mouseY = pygame.mouse.get_pos()
                mouserelX, mouserelY = pygame.mouse.get_rel()
                look_speed = .2
                bufer = glGetDoublev(GL_MODELVIEW_MATRIX)
                c = (-1 * numpy.mat(bufer[:3,:3]) * \
                    numpy.mat(bufer[3,:3]).T).reshape(3,1)
                # c is camera center in absolute coordinates,
                # we need to move it back to (0,0,0)
                # before rotating the camera
                glTranslate(c[0],c[1],c[2])
                m = bufer.flatten()
                glRotate(mouserelX * look_speed, m[1],m[5],m[9])
                glRotate(mouserelY * look_speed, m[0],m[4],m[8])

                # compensate roll
                glRotated(-math.atan2(-m[4],m[5]) * \
                    57.295779513082320876798154814105 ,m[2],m[6],m[10])
                glTranslate(-c[0],-c[1],-c[2])

        # clear buffers
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        # render cube lines
        Cube()
        # update display
        pygame.display.flip()
        # update loop sleep
        pygame.time.wait(10)

main()

