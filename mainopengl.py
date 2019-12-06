import pygame, engine_opengl, math, time, os
from engine_opengl.display import Display
from engine_opengl.eventlistener import EventListener
from engine_opengl.linedef import LineDef
from engine_opengl.solidbspnode import SolidBSPNode
from engine_opengl.camera import Camera
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *


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


# Lines, each vertex connects to the next one in CW fashion
# third element is direction its facing, when CW facing 1 = left
polygons = [
    # open room
    [
        # x, y, facing, height
        [30,  30, 0, 10],
        [300, 20, 0, 10],
        [400, 300, 0, 10],
        [30, 200, 0, 10]
    ],
    # inner col
    [
        # x, y, facing
        [50,  50, 1, 5],
        [100, 50, 1, 5],
        [75,  75, 1, 5],
        [100, 100, 1, 5],
        [50,  100, 1, 5]
    ],
    # inner room
    [
        [55, 55, 0, 5],
        [70, 55, 0, 5],
        [70, 95, 0, 5],
        [55, 95, 0, 5],
    ]
]

# Line Defs built Clockwise
allLineDefs = []
for i, v in enumerate(polygons):
    polygon = polygons[i]
    lineDefs = []
    for idx, val in enumerate(polygon):
        lineDef = LineDef()

        # first point, connect to second point
        if idx == 0:
            lineDef.asRoot(polygon[idx][0], polygon[idx][1], polygon[idx + 1][0], polygon[idx + 1][1], polygon[idx + 1][2], polygon[idx + 1][3])
            lineDefs.append(lineDef)
            allLineDefs.append(lineDef)

        # some point in the middle
        elif idx < len(polygon) - 1:
            lineDef.asChild(lineDefs[-1], polygon[idx + 1][0], polygon[idx + 1][1], polygon[idx + 1][2], polygon[idx + 1][3])
            lineDefs.append(lineDef)
            allLineDefs.append(lineDef)

        # final point, final line, connects back to first point
        elif idx == len(polygon) - 1:
            lineDef.asLeaf(lineDefs[-1], lineDefs[0], polygon[idx][2], polygon[idx][3])
            lineDefs.append(lineDef)
            allLineDefs.append(lineDef)

solidBsp = SolidBSPNode(allLineDefs)
#print(solidBsp.toText())


# TESTING WALL DRAWING
wallTest = allLineDefs[4]
# camPoint = [90, 150]
# camDirRads = 0
# camDir = engine.mathdef.toVector(camDirRads)
#camera = Camera()
#camera.worldX = 150
#camera.worldY = 60
#camera.angle = -math.pi/2


# testPoint = [60, 20]
# for lineDef in allLineDefs:
#     isBehind = lineDef.isPointBehind(testPoint[0], testPoint[1])
#     print(lineDef.start, lineDef.end, lineDef.facing, isBehind)
# print(solidBsp.inEmpty(testPoint))


pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = '1' # center window on screen
#display = Display(1920, 1080)
width = 1920
height = 1080
screen = pygame.display.set_mode((width,height), DOUBLEBUF|OPENGL) # build window with opengl
camera = Camera(75, width, height) # build camera with projection matrix
#glMatrixMode(GL_PROJECTION)
#gluPerspective(75, (1920/1080), .1, 50)
#glMatrixMode(GL_MODELVIEW) # set us into the 3d matrix
#glTranslatef(0.0, 0.0, -5.0) # move shit back
listener = EventListener()

pygame.mouse.set_visible(False)
pygame.event.set_grab(True)
font = pygame.font.Font(None, 36)

# render mode ops
mode = 0
max_modes = 4
collisionDetection = True
fullscreen = False
def mode_up():
    global mode
    mode = (mode + 1) % max_modes
listener.onKeyUp(pygame.K_UP, mode_up)
def mode_down():
    global mode
    mode = (mode - 1) % max_modes
listener.onKeyUp(pygame.K_DOWN, mode_down)
def on_x():
    global collisionDetection
    collisionDetection = not collisionDetection
listener.onKeyUp(pygame.K_x, on_x)
def on_f():
    global display
    display.toggleFullscreen()
listener.onKeyUp(pygame.K_f, on_f)

# move controls
# TODO: normalize simultaneous x and z movement
def on_a():
    global camera
    camera.strafeLeft()
listener.onKeyHold(pygame.K_a, on_a)
def on_d():
    global camera
    camera.strafeRight()
listener.onKeyHold(pygame.K_d, on_d)
def on_w():
    global camera
    camera.moveForward()
listener.onKeyHold(pygame.K_w, on_w)
def on_s():
    global camera
    camera.moveBackward()
listener.onKeyHold(pygame.K_s, on_s)
def on_mousemove(deltaX, deltaY, mouseX, mouseY):
    global camera
    camera.applyMouseMove(deltaX, deltaY)
listener.onMouseMove(on_mousemove)


def inBoundPoint(point, bounds):
    point2 = point.copy()
    point2[0] += bounds[0][0]
    point2[1] += bounds[0][1]
    return point2

def inBoundLine(line, bounds):
    line2 = []
    line2.append(line[0].copy())
    line2.append(line[1].copy())
    line2[0][0] += bounds[0][0]
    line2[0][1] += bounds[0][1]
    line2[1][0] += bounds[0][0]
    line2[1][1] += bounds[0][1]
    return line2

while True:

    listener.update()

    # RENDER 3D
    glPushMatrix() # optional

    # projection
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (width/height), .1, 50)
    # models
    glMatrixMode(GL_MODELVIEW) # set us into the 3d matrix
    #glTranslatef(0.0, 0.0, -5.0) # move shit back
    Cube()

    glPopMatrix() # optional


    # RENDER 2D - reference this: https://stackoverflow.com/questions/43130842/python-opengl-issues-displaying-2d-graphics-over-a-3d-scene
    glPushMatrix()

    # projection
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0.0, width, height, 0.0)
    #models
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glBegin(GL_TRIANGLES)
    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(0, 0)
    glVertex2f(100, 0)
    glVertex2f(0, 100)
    glEnd()

    glPopMatrix()

    # update display
    pygame.display.flip() # buffer swap


    #display.setMode2D()

    #display.start()

    ## draw floor and ceiling
    #floor = [
    #    [0, display.height / 2], [display.width, display.height / 2], [display.width, display.height], [0, display.height]
    #]
    #ceiling = [
    #    [0, 0], [display.width, 0], [display.width, display.height / 2], [0, display.height / 2]
    #]
    #display.drawPolygon(floor, (60, 60, 60), 0)
    #display.drawPolygon(ceiling, (100, 100, 100), 0)

    ## render 3D walls
    #walls = []
    #solidBsp.getWallsSorted(camera.worldX, camera.worldY, walls)
    #for i, wall in enumerate(walls):
    #    topLeft, topRight, bottomRight, bottomLeft = camera.projectWall(wall, display.width, display.height, i is 0)
    #    if topLeft:
    #        wallLines = [ topLeft, topRight, bottomRight, bottomLeft]
    #        display.drawPolygon(wallLines, wall.drawColor, 0)

    # render the top down map
    #if mode == 0:
    #    for lineDef in allLineDefs:
    #        display.drawLine([lineDef.start, lineDef.end], (0, 0, 255), 1)
    #        ln = 7
    #        mx = lineDef.mid[0]
    #        my = lineDef.mid[1]
    #        nx = lineDef.normals[lineDef.facing][0] * ln
    #        ny = lineDef.normals[lineDef.facing][1] * ln
    #        if lineDef.facing == 1:
    #            display.drawLine([ [mx, my] , [mx + nx, my + ny] ], (0, 255, 255), 1)
    #        else:
    #            display.drawLine([ [mx, my] , [mx + nx, my + ny] ], (255, 0, 255), 1)
    #if mode == 1:
    #    solidBsp.drawSegs(display)
    #if mode == 2:
    #    solidBsp.drawFaces(display, camera.worldX, camera.worldY)
    #if mode == 3:
    #    for wall in walls:
    #        display.drawLine([wall.start, wall.end], (0, 40, 255), 1)

    # render camera pos
    #angleLength = 10
    #dir = [[camera.worldX, camera.worldY], [camera.worldX + math.cos(camera.angle) * angleLength, camera.worldY + math.sin(camera.angle) * angleLength]]
    #display.drawLine(dir, (255, 100, 255), 1)
    #display.drawPoint([camera.worldX, camera.worldY], (255, 255, 255), 2)

    # test our BSP tree
    #inEmpty = solidBsp.inEmpty([camera.worldX, camera.worldY])
    #display.drawPoint([display.width - 20, 20], (0,255,60) if inEmpty else (255, 0, 0), 10)

    # render mouse
    # display.drawPoint([mouseX, mouseY], (255,255,255), 2)

    # draw our system information
    #text = font.render("collision:{} camera:[{}] m:[{}, {}]".format(collisionDetection, camera, mouseX, mouseY), 1, (50, 50, 50))
    #textpos = text.get_rect(left = 0, centery = display.height - 20)
    #display.drawText(text, textpos)

    #display.end()

    pygame.time.wait(16)
