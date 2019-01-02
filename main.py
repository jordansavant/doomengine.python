import pygame, engine, math, time
from engine.display import Display
from engine.eventlistener import EventListener
from engine.linedef import LineDef
from engine.solidbspnode import SolidBSPNode
from engine.camera import Camera

print("\n")

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
# print(solidBsp.toText())


# TESTING WALL DRAWING
wallTest = allLineDefs[4]
# camPoint = [90, 150]
# camDirRads = 0
# camDir = engine.mathdef.toVector(camDirRads)
camera = Camera()
camera.worldX = 150
camera.worldY = 60
camera.angle = -math.pi/2


# testPoint = [60, 20]
# for lineDef in allLineDefs:
#     isBehind = lineDef.isPointBehind(testPoint[0], testPoint[1])
#     print(lineDef.start, lineDef.end, lineDef.facing, isBehind)
# print(solidBsp.inEmpty(testPoint))

display = Display(1920, 1080)
listener = EventListener()
pygame.mouse.set_visible(False)
font = pygame.font.Font(None, 36)

def moveTo(x, y):
    global camera
    if not collisionDetection or solidBsp.inEmpty([x, y]):
        camera.worldX = x
        camera.worldY = y


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

def on_left():
    global camera
    # camDirRads = camDirRads - 0.1
    # camDir = engine.mathdef.toVector(camDirRads)
    camera.angle -= 0.1
listener.onKeyHold(pygame.K_LEFT, on_left)
def on_right():
    global camera
    camera.angle += 0.1
listener.onKeyHold(pygame.K_RIGHT, on_right)

def on_a():
    global camera
    potentialX = camera.worldX + math.sin(camera.angle)
    potentialY = camera.worldY - math.cos(camera.angle)
    moveTo(potentialX, potentialY)
listener.onKeyHold(pygame.K_a, on_a)
def on_d():
    global camera
    potentialX = camera.worldX - math.sin(camera.angle)
    potentialY = camera.worldY + math.cos(camera.angle)
    moveTo(potentialX, potentialY)
listener.onKeyHold(pygame.K_d, on_d)
def on_w():
    global camera
    potentialX = camera.worldX + math.cos(camera.angle)
    potentialY = camera.worldY + math.sin(camera.angle)
    moveTo(potentialX, potentialY)
listener.onKeyHold(pygame.K_w, on_w)
def on_s():
    global camera
    potentialX = camera.worldX - math.cos(camera.angle)
    potentialY = camera.worldY - math.sin(camera.angle)
    moveTo(potentialX, potentialY)
listener.onKeyHold(pygame.K_s, on_s)


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

def fncross(x1, y1, x2, y2):
    return x1 * y2 - y1 * x2

def intersect(x1, y1, x2, y2, x3, y3, x4, y4):
    x = fncross(x1, y1, x2, y2)
    y = fncross(x3, y3, x4, y4)
    det = fncross(x1 - x2, y1 - y2, x3 - x4, y3 - y4)
    x = fncross(x, x1 - x2, y, x3 - x4) / det
    y = fncross(x, y1 - y2, y, y3 - y4) / det
    return [x, y]

mouseX, mouseY = pygame.mouse.get_pos()

while True:
    listener.update()

    display.start()

    # get mouse steering
    mouseX, mouseY = pygame.mouse.get_pos()
    mouserelX, mouserelY = pygame.mouse.get_rel()
    if mouseX >= display.width - 1:
        pygame.mouse.set_pos(0, mouseY)
    elif mouseX <= 1:
        pygame.mouse.set_pos(display.width, mouseY)
    elif mouserelX <= 1000 and mouserelX >= -1000:
        camera.angle += mouserelX * 0.005
    

    # draw floor and ceiling
    floor = [
        [0, display.height / 2], [display.width, display.height / 2], [display.width, display.height], [0, display.height]
    ]
    ceiling = [
        [0, 0], [display.width, 0], [display.width, display.height / 2], [0, display.height / 2]
    ]
    display.drawPolygon(floor, (60, 60, 60), 0)
    display.drawPolygon(ceiling, (100, 100, 100), 0)

    # render 3D walls
    walls = []
    solidBsp.getWallsSorted(camera.worldX, camera.worldY, walls)
    for i, wall in enumerate(walls):
        topLeft, topRight, bottomRight, bottomLeft = camera.projectWall(wall, display.width, display.height, i is 0)
        if topLeft:
            wallLines = [ topLeft, topRight, bottomRight, bottomLeft]
            display.drawPolygon(wallLines, wall.drawColor, 0)

    # render the top down map
    if mode == 0:
        for lineDef in allLineDefs:
            display.drawLine([lineDef.start, lineDef.end], (0, 0, 255), 1)
            ln = 7
            mx = lineDef.mid[0]
            my = lineDef.mid[1]
            nx = lineDef.normals[lineDef.facing][0] * ln
            ny = lineDef.normals[lineDef.facing][1] * ln
            if lineDef.facing == 1:
                display.drawLine([ [mx, my] , [mx + nx, my + ny] ], (0, 255, 255), 1)
            else:
                display.drawLine([ [mx, my] , [mx + nx, my + ny] ], (255, 0, 255), 1)
    if mode == 1:
        solidBsp.drawSegs(display)
    if mode == 2:
        solidBsp.drawFaces(display, camera.worldX, camera.worldY)
    if mode == 3:
        for wall in walls:
            display.drawLine([wall.start, wall.end], (0, 40, 255), 1)

    # render camera pos
    angleLength = 10
    dir = [[camera.worldX, camera.worldY], [camera.worldX + math.cos(camera.angle) * angleLength, camera.worldY + math.sin(camera.angle) * angleLength]]
    display.drawLine(dir, (255, 100, 255), 1)
    display.drawPoint([camera.worldX, camera.worldY], (255, 255, 255), 2)

    # test our BSP tree
    inEmpty = solidBsp.inEmpty([camera.worldX, camera.worldY])
    display.drawPoint([display.width - 20, 20], (0,255,60) if inEmpty else (255, 0, 0), 10)

    # render mouse
    # display.drawPoint([mouseX, mouseY], (255,255,255), 2)

    # draw our system information
    text = font.render("collision:{} camera:[{}] m:[{}, {}]".format(collisionDetection, camera, mouseX, mouseY), 1, (50, 50, 50))
    textpos = text.get_rect(left = 0, centery = display.height - 20)
    display.drawText(text, textpos)

    display.end()

    time.sleep(1 / 60)