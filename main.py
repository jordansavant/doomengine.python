import pygame, engine
from engine.display import Display
from engine.eventlistener import EventListener
from engine.linedef import LineDef
from engine.solidbspnode import SolidBSPNode

print("\n")

# Lines
poly1 = [
    [50,  50],
    [100, 50],
    [75,  75],
    [100, 100],
    [50,  100]#, [200, 300]
]
# Directions (1 = CW and outward facing, 0 = CCW and inward facing)
poly1D = [ 
    1,
    1,
    1,
    1,
    1
]

# Lines
poly2 = [
    [30,  30],
    [300, 20],
    [400, 300],
    [30, 200]
]
# Directions (1 = CW and outward facing, 0 = CW and inward facing)
# Since I built poly2 CCW, direction should still be 1
poly2D = [ 
    0,
    0,
    0,
    0
]

polys = [
    poly1,
    poly2
]
polyDs = [
    poly1D,
    poly2D
]

# Line Defs built Clockwise
allLineDefs = []
for i, v in enumerate(polys):
    polyL = polys[i]
    polyD = polyDs[i]
    lineDefs = []
    for idx, val in enumerate(polyL):
        lineDef = LineDef()

        # first point, connect to second point
        if idx == 0:
            lineDef.asRoot(polyL[idx][0], polyL[idx][1], polyL[idx + 1][0], polyL[idx + 1][1], polyD[idx])
            lineDefs.append(lineDef)
            allLineDefs.append(lineDef)

        # some point in the middle
        elif idx < len(polyL) - 1:
            lineDef.asChild(lineDefs[-1], polyL[idx + 1][0], polyL[idx + 1][1], polyD[idx])
            lineDefs.append(lineDef)
            allLineDefs.append(lineDef)
        
        # final point, final line, connects back to first point
        elif idx == len(polyL) - 1:
            lineDef.asLeaf(lineDefs[-1], lineDefs[0], polyD[idx])
            lineDefs.append(lineDef)
            allLineDefs.append(lineDef)

solidBsp = SolidBSPNode(allLineDefs)
testPoint = [60, 20]
print(solidBsp.toText())


for lineDef in allLineDefs:
    isBehind = lineDef.isPointBehind(testPoint[0], testPoint[1])
    print(lineDef.start, lineDef.end, lineDef.facing, isBehind)

print(solidBsp.inEmpty(testPoint))

display = Display(1280, 720)
listener = EventListener()



font = pygame.font.Font(None, 36)
    

# render mode ops
mode = 0
max_modes = 3
def mode_swap():
    global mode
    mode = (mode + 1) % max_modes

# register callback function for changing the render mode
listener.onKeyUp(pygame.K_UP, mode_swap)

while True:
    listener.update()

    display.start()

    # render the polygons
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
        solidBsp.draw(display)

    display.drawPoint(testPoint, (0, 0, 255), 2)

    mx, my = pygame.mouse.get_pos()
    text = font.render("{}, {}".format(mx, my), 1, (50, 50, 50))
    textpos = text.get_rect(centerx = display.width / 2, centery = display.height/2)
    display.drawText(text, textpos)

    inEmpty = solidBsp.inEmpty([mx, my])
    display.drawPoint([mx, my], (0,255,255) if inEmpty else (255, 0, 0), 4)

    display.end()