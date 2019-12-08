import pygame, engine_opengl, math, time, sys
from engine_opengl.display import Display
from engine_opengl.eventlistener import EventListener
from engine_opengl.linedef import LineDef
from engine_opengl.solidbspnode import SolidBSPNode
from engine_opengl.camera import Camera
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

#--- 3D projection function
def render3d():

    global width, height

    ### clear buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glViewport(0, 0, width, height)

    ### projection mode
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(width)/float(height), 0.1, 100.0)

    ### modelview mode
    glMatrixMode(GL_MODELVIEW)

    ### setup 3d shader
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)

#--- 2D projection function
def render2d():

    global width, height

    ### projection mode
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0.0, width, height, 0.0)

    ### modelview mode
    glMatrixMode(GL_MODELVIEW)

    ### setup 2d shader
    glDisable(GL_DEPTH_TEST)

#--- reshape function
def reshape(new_width, new_height):

    global width, height

    ### apply new window size
    width = new_width
    height = new_height

#--- 3D cube function
def scene3d():

    ### setup polygon location & orientation
    glTranslatef(0.0, 0.0, -6.0)
    glRotatef(30, 1.0, 0.0, 0.0)
    glRotatef(0, 1.0, 1.0, 0.0)
    glRotatef(30, 0.0, 0.0, 1.0)

    ### draw cube
    glBegin(GL_QUADS)

    glColor3f(0.0,1.0,0.0)
    glVertex3f( 1.0, 1.0,-1.0)
    glVertex3f(-1.0, 1.0,-1.0)
    glVertex3f(-1.0, 1.0, 1.0)
    glVertex3f( 1.0, 1.0, 1.0)

    glColor3f(1.0,0.0,0.0)
    glVertex3f( 1.0,-1.0, 1.0)
    glVertex3f(-1.0,-1.0, 1.0)
    glVertex3f(-1.0,-1.0,-1.0)
    glVertex3f( 1.0,-1.0,-1.0)

    glColor3f(0.0,1.0,1.0)
    glVertex3f( 1.0, 1.0, 1.0)
    glVertex3f(-1.0, 1.0, 1.0)
    glVertex3f(-1.0,-1.0, 1.0)
    glVertex3f( 1.0,-1.0, 1.0)

    glColor3f(1.0,1.0,0.0)
    glVertex3f( 1.0,-1.0,-1.0)
    glVertex3f(-1.0,-1.0,-1.0)
    glVertex3f(-1.0, 1.0,-1.0)
    glVertex3f( 1.0, 1.0,-1.0)

    glColor3f(0.0,0.0,1.0)
    glVertex3f(-1.0, 1.0, 1.0)
    glVertex3f(-1.0, 1.0,-1.0)
    glVertex3f(-1.0,-1.0,-1.0)
    glVertex3f(-1.0,-1.0, 1.0)

    glColor3f(1.0,0.0,1.0)
    glVertex3f( 1.0, 1.0,-1.0)
    glVertex3f( 1.0, 1.0, 1.0)
    glVertex3f( 1.0,-1.0, 1.0)
    glVertex3f( 1.0,-1.0,-1.0)

    glEnd()

#--- 2D triangle function
def scene2d():

    ### draw triangle
    glBegin(GL_TRIANGLES)

    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(0, 0)
    glVertex2f(100, 0)
    glVertex2f(0, 100)

    glEnd()

#--- draw function
def draw():

    ### 3D scene
    render3d()
    scene3d()

    ### 2D scene
    glPushMatrix()

    render2d()
    scene2d()

    glPopMatrix()

    ### swap buffers
    glutSwapBuffers()

#--- main loop function
def main():

    window = 0

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(640,480)
    glutInitWindowPosition(200,200)

    window = glutCreateWindow(b'OpenGL Python HUD')

    glutReshapeFunc(reshape)
    glutDisplayFunc(draw)
    glutIdleFunc(draw)
    glutMainLoop()

main()

