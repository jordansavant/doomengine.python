import pygame, engine, math, time
from engine.display import Display
from engine.eventlistener import EventListener
from engine.linedef import LineDef
from engine.solidbspnode import SolidBSPNode

print("\n")


# TESTING WALL DRAWING
wallTest = [[70, 20], [70, 70]]
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


bounds = [
    [0, 0],
    [99, 0],
    [99, 109],
    [0, 109]
]

display.scale = 2


while True:
    listener.update()

    display.start()
    
    px = camPoint[0]
    py = camPoint[1]
    angle = camDirRads
    
    # Render top down version of our map
    display.drawLines(bounds, (0, 0, 200), 2, True)

    # Render wall
    display.drawLine(wallTest, (255, 255, 0), 2)

    # Render player angle
    display.drawLine([[px, py], [px + math.cos(angle) * 5, py + math.sin(angle) * 5]], (100, 100, 100), 2)

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