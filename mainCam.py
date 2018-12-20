import pygame, engine, math, time
from engine.display import Display
from engine.eventlistener import EventListener
from engine.linedef import LineDef
from engine.solidbspnode import SolidBSPNode

print("\n")


# TESTING WALL DRAWING
wall = [[70, 20], [70, 70]]
camPoint = [50, 50]
camDirRads = 0
camDir = engine.mathdef.toVector(camDirRads)

display = Display(640, 480)
listener = EventListener()
pygame.mouse.set_visible(False)
font = pygame.font.Font(None, 36)

def on_left():
    global camDir, camDirRads
    camDirRads = camDirRads - 0.1
    camDir = engine.mathdef.toVector(camDirRads)
listener.onKeyHold(pygame.K_LEFT, on_left)
def on_right():
    global camDir, camDirRads
    camDirRads = camDirRads + 0.1
    camDir = engine.mathdef.toVector(camDirRads)
listener.onKeyHold(pygame.K_RIGHT, on_right)

def on_a():
    global camPoint
    camPoint[0] = camPoint[0] + math.sin(camDirRads)
    camPoint[1] = camPoint[1] - math.cos(camDirRads)
listener.onKeyHold(pygame.K_a, on_a)
def on_d():
    global camPoint
    camPoint[0] = camPoint[0] - math.sin(camDirRads)
    camPoint[1] = camPoint[1] + math.cos(camDirRads)
listener.onKeyHold(pygame.K_d, on_d)
def on_w():
    global camPoint
    camPoint[0] = camPoint[0] + math.cos(camDirRads)
    camPoint[1] = camPoint[1] + math.sin(camDirRads)
listener.onKeyHold(pygame.K_w, on_w)
def on_s():
    global camPoint
    camPoint[0] = camPoint[0] - math.cos(camDirRads)
    camPoint[1] = camPoint[1] - math.sin(camDirRads)
listener.onKeyHold(pygame.K_s, on_s)


tdBounds = [
    [4, 40],
    [103, 40],
    [103, 149],
    [4, 149]
]

pjBounds = [
    [109, 40],
    [208, 40],
    [208, 149],
    [109, 149]
]

fpBounds = [
    [214, 40],
    [315, 40],
    [315, 149],
    [214, 149]
]

display.scale = 2

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
    
    px = camPoint[0]
    py = camPoint[1]
    angle = camDirRads

    # TOP DOWN
    
    # Render frame
    display.drawLines(tdBounds, (0, 0, 200), 2, True)

    # Render wall
    tdWall = inBoundLine(wall, tdBounds)
    display.drawLine(tdWall, (255, 255, 0), 2)

    # Render player angle
    dir = [[px, py], [px + math.cos(angle) * 5, py + math.sin(angle) * 5]]
    tdDir = inBoundLine(dir, tdBounds)
    display.drawLine(tdDir, (100, 100, 100), 2)

    # Render player pos
    tdCamPoint = inBoundPoint(camPoint, tdBounds)
    display.drawPoint(tdCamPoint, (255, 255, 255), 2)


    # PROJECTED

    # Render frame
    display.drawLines(pjBounds, (0, 200, 0), 2, True)

    # Transform vertices relative to player
    tx1 = wall[0][0] - px
    ty1 = wall[0][1] - py
    tx2 = wall[1][0] - px
    ty2 = wall[1][1] - py

    # Rotate them around the players view
    tz1 = tx1 * math.cos(angle) + ty1 * math.sin(angle)
    tz2 = tx2 * math.cos(angle) + ty2 * math.sin(angle)
    tx1 = tx1 * math.sin(angle) - ty1 * math.cos(angle)
    tx2 = tx2 * math.sin(angle) - ty2 * math.cos(angle)

    # Render wall
    pjWall = [[50 - tx1, 50 - tz1], [50 - tx2, 50 - tz2]]
    pjWall = inBoundLine(pjWall, pjBounds)
    display.drawLine(pjWall, (255, 255, 0), 2)

    # Render player angle
    pjDir = [[50, 50], [50, 45]]
    pjDir = inBoundLine(pjDir, pjBounds)
    display.drawLine(pjDir, (100, 100, 100), 2)

    # Render player pos
    pjCamPoint = [50, 50]
    pjCamPoint = inBoundPoint(pjCamPoint, pjBounds)
    display.drawPoint(pjCamPoint, (255, 255, 255), 2)


    # PERSPECTIVE TRANSFORMED

    # Render frame
    display.drawLines(fpBounds, (0, 200, 200), 2, True)

    # Clip
    # determine clipping, if both z's < 0 its totally behind
	# if only 1 is negative it can be clipped
    if tz1 > 0 or tz2 > 0:
        # if line crosses the players view plane clip it
        # i think the last two are set by refs
        i1 = intersect(tx1, tz1, tx2, tz2, -0.0001, 0.0001, -20, 5)
        ix1 = i1[0]
        iz1 = i1[1]
        i2 = intersect(tx1, tz1, tx2, tz2, 0.0001, 0.0001, 20, 5)
        ix2 = i2[0]
        iz2 = i2[1]
        if tz1 <= 0:
            if iz1 > 0:
                tx1 = ix1
                tz1 = iz1
            else:
                tx1 = ix2
                tz1 = iz2
        if tz2 <= 0:
            if iz1 > 0:
                tx2 = ix1
                tz2 = iz1
            else:
                tx2 = ix2
                tz2 = iz2

    if (tz1 > 0 and tz2 > 0):

        # Transform
        x1 = -tx1 * 16 / tz1
        y1a = -50 / tz1
        y1b = 50 / tz1
        x2 = -tx2 * 16 / tz2
        y2a = -50 / tz2
        y2b = 50 / tz2

        print(tx1, tx2, tz1, tz2)

        # Render
        topLine = [[50 + x1, 50 + y1a], [50 + x2, 50 + y2a]]
        bottomLine = [[50 + x1, 50 + y1b], [50 + x2, 50 + y2b]]
        leftLine = [[50 + x1, 50 + y1a], [50 + x1, 50 + y1b]]
        rightLine = [[50 + x2, 50 + y2a], [50 + x2, 50 + y2b]]
        
        fpTopLine = inBoundLine(topLine, fpBounds)
        fpBottomLine = inBoundLine(bottomLine, fpBounds)
        fpLeftLine = inBoundLine(leftLine, fpBounds)
        fpRightLine = inBoundLine(rightLine, fpBounds)
        display.drawLine(fpTopLine, (255, 255, 0), 2)
        display.drawLine(fpBottomLine, (255, 255, 0), 2)
        display.drawLine(fpLeftLine, (255, 255, 0), 2)
        display.drawLine(fpRightLine, (255, 255, 0), 2)



    time.sleep(0.016666667)

    ## render camera
    #ll = 40
    #display.drawLine([ camPoint, [camPoint[0] + camDir[0] * ll, camPoint[1] + camDir[1] * ll] ], (175, 175, 175), 1)
    #display.drawLine([ camPoint, [camPoint[0] + camR[0] * ll, camPoint[1] + camR[1] * ll] ], (255, 0, 0), 1)
    #display.drawLine([ camPoint, [camPoint[0] + camL[0] * ll, camPoint[1] + camL[1] * ll] ], (255, 0, 0), 1)
    #display.drawPoint(camPoint, (255, 255, 255), 2)

    ## render wall
    #display.drawLine(wallTest, (255, 255, 0), 2)

    ## Render our projection

    #leftSide = [wallTest[0][0], wallTest[0][1]]
    #leftSideDistance = engine.mathdef.distance2d(camPoint[0], camPoint[1], leftSide[0], leftSide[1])
    #leftSideDirection = [wallTest[0][0] - camPoint[0], wallTest[0][1] - camPoint[1]]
    #leftSideRadians = engine.mathdef.toRadians(leftSideDirection[0], leftSideDirection[1])
    #leftCameraRadians = engine.mathdef.toRadians(camL[0], camL[1])

    #rightSide = [wallTest[1][0], wallTest[1][1]]
    #rightSideDistance = engine.mathdef.distance2d(camPoint[0], camPoint[1], rightSide[0], rightSide[1])
    #rightSideDirection = [wallTest[1][0] - camPoint[0], wallTest[1][1] - camPoint[1]]
    #rightSideRadians = engine.mathdef.toRadians(rightSideDirection[0], rightSideDirection[1])
    #rightCameraRadians = engine.mathdef.toRadians(camR[0], camR[1])

    ##leftIntersection = engine.mathdef.intersection2d(camPoint, [camPoint[0] + camL[0], camPoint[1] + camL[1]], wallTest.start, wallTest.end)
    ##rightIntersection = engine.mathdef.intersection2d(camPoint, [camPoint[0] + camR[0], camPoint[1] + camR[1]], wallTest.start, wallTest.end)
    ##leftIntersectionDistance = engine.mathdef.distance2d(camPoint[0], camPoint[1], leftIntersection[0], leftIntersection[1])
    ##rightIntersectionDistance = engine.mathdef.distance2d(camPoint[0], camPoint[1], rightIntersection[0], rightIntersection[1])

    #cameraCos = math.cos(camDirRads)# camDir[0]
    #cameraSin = math.sin(camDirRads)# camDir[1]
    #cameraX = camPoint[0]
    #cameraY = 0
    #cameraZ = camPoint[1]
    #screenW = display.width
    #screenH = display.height

    #x = leftSide[0]
    #y = 0
    #z = leftSide[1]
    #s3L = s3proj(x, y, z, cameraCos, cameraSin, cameraX, cameraY, cameraZ, screenW, screenH)

    #x = rightSide[0]
    #y = 0
    #z = rightSide[1]
    #s3R = s3proj(x, y, z, cameraCos, cameraSin, cameraX, cameraY, cameraZ, screenW, screenH)
    #print(s3L, "|", s3R)

    ## visualize position
    #display.drawPoint([s3L[0],display.height/2], (0, 0, 255), 3)
    #display.drawPoint([s3R[0],display.height/2], (0, 255, 0), 3)

    # draw our position information
    mx, my = pygame.mouse.get_pos()
    text = font.render("{}, {}".format(mx, my), 1, (50, 50, 50))
    textpos = text.get_rect(centerx = display.width / 2, centery = display.height/2)
    display.drawText(text, textpos)

    display.end()