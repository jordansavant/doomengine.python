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
        # x, y, facing
        [30,  30, 0],
        [300, 20, 0],
        [400, 300, 0],
        [30, 200, 0]
    ],
    # inner col
    [
        # x, y, facing
        [50,  50, 1],
        [100, 50, 1],
        [75,  75, 1],
        [100, 100, 1],
        [50,  100, 1]
    ],
    # inner room
    [
        [55, 55, 0],
        [70, 55, 0],
        [70, 95, 0],
        [55, 95, 0],
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
            lineDef.asRoot(polygon[idx][0], polygon[idx][1], polygon[idx + 1][0], polygon[idx + 1][1], polygon[idx + 1][2])
            lineDefs.append(lineDef)
            allLineDefs.append(lineDef)

        # some point in the middle
        elif idx < len(polygon) - 1:
            lineDef.asChild(lineDefs[-1], polygon[idx + 1][0], polygon[idx + 1][1], polygon[idx + 1][2])
            lineDefs.append(lineDef)
            allLineDefs.append(lineDef)
        
        # final point, final line, connects back to first point
        elif idx == len(polygon) - 1:
            lineDef.asLeaf(lineDefs[-1], lineDefs[0], polygon[idx][2])
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

display = Display(1280, 720)
listener = EventListener()
pygame.mouse.set_visible(False)
font = pygame.font.Font(None, 36)
    
# render mode ops
mode = 0
max_modes = 4
def mode_up():
    global mode
    mode = (mode + 1) % max_modes
listener.onKeyUp(pygame.K_UP, mode_up)
def mode_down():
    global mode
    mode = (mode - 1) % max_modes
listener.onKeyUp(pygame.K_DOWN, mode_down)

def on_left():
    global camera
    # camDirRads = camDirRads - 0.1
    # camDir = engine.mathdef.toVector(camDirRads)
    camera.angle -= 0.1
listener.onKeyHold(pygame.K_LEFT, on_left)
def on_right():
    global camera
    # camDirRads = camDirRads + 0.1
    # camDir = engine.mathdef.toVector(camDirRads)
    camera.angle += 0.1
listener.onKeyHold(pygame.K_RIGHT, on_right)
def on_a():
    global camera
    camera.worldX += math.sin(camera.angle)
    camera.worldY -= math.cos(camera.angle)
    # camPoint[0] = camPoint[0] + math.sin(camDirRads)
    # camPoint[1] = camPoint[1] - math.cos(camDirRads)
listener.onKeyHold(pygame.K_a, on_a)
def on_d():
    global camera
    camera.worldX -= math.sin(camera.angle)
    camera.worldY += math.cos(camera.angle)
    # camPoint[0] = camPoint[0] - math.sin(camDirRads)
    # camPoint[1] = camPoint[1] + math.cos(camDirRads)
listener.onKeyHold(pygame.K_d, on_d)
def on_w():
    global camera
    camera.worldX += math.cos(camera.angle)
    camera.worldY += math.sin(camera.angle)
    # camPoint[0] = camPoint[0] + math.cos(camDirRads)
    # camPoint[1] = camPoint[1] + math.sin(camDirRads)
listener.onKeyHold(pygame.K_w, on_w)
def on_s():
    global camera
    camera.worldX -= math.cos(camera.angle)
    camera.worldY -= math.sin(camera.angle)
    # camPoint[0] = camPoint[0] - math.cos(camDirRads)
    # camPoint[1] = camPoint[1] - math.sin(camDirRads)
listener.onKeyHold(pygame.K_s, on_s)

fpvpX = 500
fpvpY = 100
fpvpW = 500
fpvpH = 300
fpvp = [
        [fpvpX, fpvpY],
        [fpvpX + fpvpW, fpvpY],
        [fpvpX + fpvpW, fpvpY + fpvpH],
        [fpvpX, fpvpY + fpvpH],
]

tdBounds = [
    [500 + 4, 40],
    [500 + 103, 40],
    [500 + 103, 149],
    [500 + 4, 149]
]

pjBounds = [
    [500 + 109, 40],
    [500 + 208, 40],
    [500 + 208, 149],
    [500 + 109, 149]
]


surfaceWidth = 320
surfaceHeight = 180
fpBounds = [
    [500 + 214, 40],
    [500 + 214 + surfaceWidth, 40],
    [500 + 214 + surfaceWidth, 40 + surfaceHeight],
    [500 + 214, 40 + surfaceHeight]
]


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


while True:
    listener.update()

    display.start()
    

    walls = []
    solidBsp.getWallsSorted(camera.worldX, camera.worldY, walls)

    # render the polygons directly
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

    mx, my = pygame.mouse.get_pos()

    # render the tree
    if mode == 1:
        solidBsp.drawSegs(display)
    if mode == 2:
        solidBsp.drawFaces(display, camera.worldX, camera.worldY)
    if mode == 3:
        for wall in walls:
            display.drawLine([wall.start, wall.end], (0, 40, 255), 1)
        
    

    # render 3D walls
    for i, wall in enumerate(walls):
        topLeft, topRight, bottomRight, bottomLeft = camera.projectWall(wall, display.width, display.height, i is 0)
        if topLeft:
            wallLines = [ topLeft, topRight, bottomRight, bottomLeft]
            display.drawPolygon(wallLines, wall.drawColor, 0)
    # solidBsp.drawWalls(camera, display)

    # render camera
    angleLength = 10
    dir = [[camera.worldX, camera.worldY], [camera.worldX + math.cos(camera.angle) * angleLength, camera.worldY + math.sin(camera.angle) * angleLength]]
    display.drawLine(dir, (255, 100, 255), 1)
    display.drawPoint([camera.worldX, camera.worldY], (255, 255, 255), 2)

    '''
    # ========================
    # Top Down Perspective
    
    # Render frame
    display.drawLines(tdBounds, (150, 0, 150), 2, True)
    # Render wall
    tdWall = inBoundLine(wall, tdBounds)
    display.drawLine(tdWall, (255, 50, 255), 2)
    # Render player angle
    dir = [[camera.worldX, camera.worldY], [camera.worldX + math.cos(camera.angle) * angleLength, camera.worldY + math.sin(camera.angle) * angleLength]]
    tdDir = inBoundLine(dir, tdBounds)
    display.drawLine(tdDir, (255, 100, 255), 1)
    # Render player pos
    tdCamPoint = inBoundPoint([camera.worldX, camera.worldY], tdBounds)
    display.drawPoint(tdCamPoint, (255, 255, 255), 2)

    # ========================
    # Transformed Perspected

    # Render frame
    display.drawLines(pjBounds, (150, 150, 0), 2, True)
    # Transform vertices relative to player
    (tx1, ty1, tz1, tx2, ty2, tz2) = camera.transformWall(wallTest)
    # Render wall
    pjWall = [[50 - tx1, 50 - tz1], [50 - tx2, 50 - tz2]]
    pjWall = inBoundLine(pjWall, pjBounds)
    display.drawLine(pjWall, (255, 255, 50), 2)
    # Render player angle
    pjDir = [[50, 50], [50, 50 - angleLength]]
    pjDir = inBoundLine(pjDir, pjBounds)
    display.drawLine(pjDir, (255, 255, 100), 1)
    # Render player pos
    pjCamPoint = [50, 50]
    pjCamPoint = inBoundPoint(pjCamPoint, pjBounds)
    display.drawPoint(pjCamPoint, (255, 255, 255), 2)
    

    # ========================
    # FPS Perspective

    # Render frame
    display.drawLines(fpBounds, (0, 150, 150), 2, True)
    # Render Projection
    topLeft, topRight, bottomRight, bottomLeft = camera.projectWall(wallTest, surfaceWidth, surfaceHeight)
    if topLeft is not None:
        fpLines = [
            inBoundPoint(topLeft, fpBounds),
            inBoundPoint(topRight, fpBounds),
            inBoundPoint(bottomRight, fpBounds),
            inBoundPoint(bottomLeft, fpBounds)
        ]
        display.drawPolygon(fpLines, (0, 255, 255), 0)
    '''

    # draw our position information
    text = font.render("{}, {}".format(mx, my), 1, (50, 50, 50))
    textpos = text.get_rect(centerx = display.width - 60, centery = display.height - 20)
    display.drawText(text, textpos)

    # test our BSP tree
    inEmpty = solidBsp.inEmpty([mx, my])
    display.drawPoint([mx, my], (0,255,255) if inEmpty else (255, 0, 0), 4)

    display.end()

    time.sleep(1 / 60)