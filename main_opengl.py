import pygame, engine_opengl, math, os
from engine_opengl.eventlistener import EventListener
from engine_opengl.linedef import LineDef
from engine_opengl.solidbspnode import SolidBSPNode
from engine_opengl.camera import Camera
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *


# CUBE DATA
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

def Cube(x, y, z):
    # render colored surfaces as quads
    glBegin(GL_QUADS)
    for surface in surfaces:
        i = 0
        for vertex in surface:
            i+=1
            v = vertices[vertex]
            glColor3fv(colors[i])
            glVertex3f(v[0] + x, v[1] + y, v[2] + z)
    glEnd()

    # render lines between vertices
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            v = vertices[vertex]
            glVertex3f(v[0] + x, v[1] + y, v[2] + z)
    glEnd()

# MAP ROOMS
# Lines, each vertex connects to the next one in CW fashion
# third element is direction its facing, when CW facing 1 = left
polygons = [
    # open room
    [
        # x, z, facing, height (y)
        [30,  30, 0, 10],
        [300, 20, 0, 10],
        [400, 300, 0, 10],
        [30, 200, 0, 10]
    ],
    # inner col
    [
        # x, z, facing, height (y)
        [50,  50, 1, 5],
        [100, 50, 1, 5],
        [75,  75, 1, 5],
        [100, 100, 1, 5],
        [50,  100, 1, 5]
    ],
    # inner room
    [
        # x, z, facing, height (y)
        [55, 55, 0, 5],
        [70, 55, 0, 5],
        [70, 95, 0, 5],
        [55, 95, 0, 5],
    ],
    # concave room 2
    [
        # x, z, facing, height (y)
        [125, 55, 1, 7],
        [170, 55, 1, 7],
        [170, 95, 1, 7],
        [155, 95, 1, 7],
        [155, 90, 1, 7],
        [165, 90, 1, 7],
        [165, 60, 1, 7],
        [140, 60, 1, 7],
        [135, 70, 1, 7],
    ],
    # room, without another outward room inside
    [
        [180, 180, 1, 1],
        [230, 180, 1, 1],
        [230, 230, 1, 1],
        [180, 230, 1, 1],
    ],
    [
        [190, 190, 1, 3],
        [220, 190, 1, 3],
        [220, 220, 1, 3],
        [190, 220, 1, 3],
    ],
]

# Create SolidBSP for Level
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
print(solidBsp.toText(), flush=True)

# GAME SETUP
pygame.init()

# get os resolution
displayInfo = pygame.display.Info()
resolutionWidth = displayInfo.current_w
resolutionHeight = displayInfo.current_h

# start with this resolution in windowed
targetWidth = 1280
targetHeight = 720
displayWidth = targetWidth
displayHeight = targetHeight

os.environ['SDL_VIDEO_CENTERED'] = '1' # center window on screen
screen = pygame.display.set_mode((displayWidth, displayHeight), DOUBLEBUF|OPENGL) # build window with opengl
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)
glEnable(GL_BLEND); # allows for alpha transparency on color
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
font = pygame.font.Font(None, 36) # TODO not sure if we can use this
listener = EventListener()
camera = Camera(solidBsp)

# set base camera application for matrix
glMatrixMode(GL_MODELVIEW) # set us into the 3d matrix
camera.setPosition(110, 2, 95);
camera.setYaw(-math.pi/2)

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
def on_m():
    global camera
    camera.toggleMouseLook()
listener.onKeyUp(pygame.K_m, on_m)
def on_x():
    global camera
    camera.collisionDetection = not camera.collisionDetection
listener.onKeyUp(pygame.K_x, on_x)
def on_f():
    global fullscreen, screen, displayWidth, displayHeight
    global resolutionWidth, resolutionHeight, targetWidth, targetHeight
    fullscreen = not fullscreen
    # get world model matrix
    m = glGetDoublev(GL_MODELVIEW_MATRIX).flatten()
    if fullscreen:
        displayWidth, displayHeight = resolutionWidth, resolutionHeight
        screen = pygame.display.set_mode((displayWidth,displayHeight), DOUBLEBUF|OPENGL|FULLSCREEN) # build window with opengl
    else:
        displayWidth, displayHeight = targetWidth, targetHeight
        screen = pygame.display.set_mode((displayWidth,displayHeight), DOUBLEBUF|OPENGL) # build window with opengl
    # if fullscreen take over mouse
    #pygame.mouse.set_visible(not fullscreen)
    #pygame.event.set_grab(fullscreen)
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    # reapply window matrix
    glLoadMatrixf(m)
listener.onKeyUp(pygame.K_f, on_f)

# move controls
listener.onKeyHold(pygame.K_a, camera.strafeLeft)
listener.onKeyHold(pygame.K_d, camera.strafeRight)
listener.onKeyHold(pygame.K_w, camera.moveForward)
listener.onKeyHold(pygame.K_s, camera.moveBackward)
listener.onMouseMove(camera.applyMouseMove)

# info
print("m (mouselook)")
print("x (noclip)")
print("f (fullscreen)")
print("up_arrow (map mode up)")
print("down_arrow (map mode down)")
print("wasd (movement)", flush=True)


def drawLine(start, end, width, r, g, b, a):
    glLineWidth(width)
    glColor4f(r, g, b, a)
    glBegin(GL_LINES)
    glVertex2f(start[0], start[1])
    glVertex2f(end[0], end[1])
    glEnd()

def drawPoint(pos, radius, r, g, b, a):
    glColor4f(r, g, b, a)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(pos[0], pos[1]);
    for angle in range(10, 3610, 2):
        angle = angle / 10 # convert back down to degrees
        x2 = pos[0] + math.sin(angle) * radius;
        y2 = pos[1] + math.cos(angle) * radius;
        glVertex2f(x2, y2);
    glEnd()

def drawHud(offsetX, offsetY, width, height, mode, camera, allLineDefs, walls):
    # wall lines
    # walls are position in with start and in in the x and z coordinates
    if mode == 0:
        for lineDef in allLineDefs:
            # draw wall
            mapStart = [lineDef.start[0] + offsetX, lineDef.start[1] + offsetY]
            mapEnd = [lineDef.end[0] + offsetX, lineDef.end[1] + offsetY]
            drawLine(mapStart, mapEnd, 1, 0.0, 0.0, 1.0, 1.0)
            # draw facing dir
            ln = 7
            mx = lineDef.mid[0]
            my = lineDef.mid[1]
            nx = lineDef.normals[lineDef.facing][0] * ln
            ny = lineDef.normals[lineDef.facing][1] * ln
            if lineDef.facing == 1:
                drawLine([mx + offsetX, my + offsetY], [mx + nx + offsetX, my + ny + offsetY], 2, 0.0, 1.0, 1.0, 1.0)
            else:
                drawLine([mx + offsetX, my + offsetY], [mx + nx + offsetX, my + ny + offsetY], 2, 1.0, 0.0, 1.0, 1.0)
    if mode == 1:
        solidBsp.drawSegs(drawLine, offsetX, offsetY)
    if mode == 2:
        solidBsp.drawFaces(drawLine, camera.worldPos[0], camera.worldPos[2], offsetX, offsetY)
    if mode == 3:
        for wall in walls:
            start = [wall.start[0] + offsetX, wall.start[1] + offsetY];
            end = [wall.end[0] + offsetX, wall.end[1] + offsetY];
            drawLine(start, end, 1, 0, .3, 1, 1)

    # camera
    angleLength = 10
    camOrigin = [camera.worldPos[0] + offsetX, camera.worldPos[2] + offsetY] # mapX is worldX, mapY is worldZ
    camNeedle = [camOrigin[0] + math.cos(camera.yaw - math.pi/2) * angleLength, camOrigin[1] + math.sin(camera.yaw - math.pi/2) * angleLength]
    # yaw at 0 is straight down the positive z, which is down mapY
    drawLine(camOrigin, camNeedle, 1, 1, .5, 1, 1)
    drawPoint(camOrigin, 2, 1, 1, 1, 1)

    # render crosshair
    drawLine([displayWidth/2, displayHeight/2 - 8], [displayWidth/2, displayHeight/2 - 2], 2, 1, .3, .3, 1)
    drawLine([displayWidth/2, displayHeight/2 + 2], [displayWidth/2, displayHeight/2 + 8], 2, 1, .3, .3, 1)
    drawLine([displayWidth/2 - 8, displayHeight/2], [displayWidth/2 - 2, displayHeight/2], 2, 1, .3, .3, 1)
    drawLine([displayWidth/2 + 2, displayHeight/2], [displayWidth/2 + 8, displayHeight/2], 2, 1, .3, .3, 1)

    # collision flag dot
    if camera.collisionDetection:
        drawPoint([displayWidth - 50, 50], 10, 0, 1, 0, 1)
    else:
        drawPoint([displayWidth - 50, 50], 10, 1, 0, 0, 1)

def drawWalls(walls, camera):
    for i, wall in enumerate(walls):
        glBegin(GL_QUADS)
        c = wall.drawColor
        glColor3f(c[0]/255, c[1]/255, c[2]/255)
        glVertex3f(wall.start[0],   0,              wall.start[1]) # low lef
        glVertex3f(wall.start[0],   wall.height,    wall.start[1]) # up lef
        glVertex3f(wall.end[0],     wall.height,    wall.end[1]) # up rig
        glVertex3f(wall.end[0],     0,              wall.end[1]) # up lef
        glEnd()

def update():
    listener.update()
    camera.update()

def draw():
    # sort walls around camera x and z
    walls = []
    solidBsp.getWallsSorted(camera.worldPos[0], camera.worldPos[2], walls)


    # RENDER 3D
    glPushMatrix() # copies matrix below stack (in this case, our base camera matrix transformation)

    # projection
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glViewport(0, 0, displayWidth, displayHeight)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (displayWidth/displayHeight), 0.00001, 5000)
    # models
    glMatrixMode(GL_MODELVIEW) # set us into the 3d matrix

    #Cube(20, 0, 20)
    #Cube(-3, 3, 5)
    #Cube(0, 0, 10)
    #Cube(3, -3, 15)

    drawWalls(walls, camera)

    glPopMatrix()
    # END 3D


    # RENDER 2D - reference this: https://stackoverflow.com/questions/43130842/python-opengl-issues-displaying-2d-graphics-over-a-3d-scene
    glPushMatrix()

    # projection
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0.0, displayWidth, displayHeight, 0.0)
    # models
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    drawHud(20, 20, 400, 300, mode, camera, allLineDefs, walls)

    glPopMatrix()
    # END 2D

    # update display
    pygame.display.flip() # buffer swap

timer = 0
actualTime = pygame.time.get_ticks() # ms
FPS = 60
dt = int(1 / FPS * 1000) # 60 fps in ms
updateCounter = 0
drawCounter = 0
while True:

    # UPDATE at fixed intervals
    newTime = pygame.time.get_ticks() # ms
    frameTime = newTime - actualTime
    if frameTime > 250:
        fameTime = 250 # avoid spiral of death
    timer += frameTime
    while timer >= dt:
        # TODO pass delta time in seconds
        update()
        updateCounter += 1
        timer -= dt

    draw()
    drawCounter += 1

    actualTime = newTime # ms
    #pygame.time.wait(16) # dinky 60fps

    # OLD RENDERING
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

    #pygame.time.wait(16)
