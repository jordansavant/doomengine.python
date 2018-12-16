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
testPoint = [60, 75]
print(solidBsp.toText())


for lineDef in allLineDefs:
    isBehind = engine.mathdef.pointBehindSegment(testPoint, lineDef.start, lineDef.end) and lineDef.facing == 1
    print(lineDef.start, lineDef.end, lineDef.facing, isBehind, lineDef.normals)


# testing ray intersection
print("ray test")
ray1 = allLineDefs[0]
ray2 = allLineDefs[6]
print ([ray1.start, ray1.end], [ray2.start, ray2.end])
splits = ray1.split(ray2)

display = Display(1280, 720)
listener = EventListener()
    

# render mode ops
mode = 0
max_modes = 3
def mode_swap():
    global mode
    mode = (mode + 1) % max_modes
    print(mode)

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
            # n1x = lineDef.normals[0][0] * ln
            # n1y = lineDef.normals[0][1] * ln
            # n2x = lineDef.normals[1][0] * ln
            # n2y = lineDef.normals[1][1] * ln
            # display.drawLine([ [mx, my] , [mx + n1x, my + n1y] ], (0, 255, 255), 2)
            # display.drawLine([ [mx, my] , [mx + n2x, my + n2y] ], (255, 0, 255), 2)
        display.drawPoint(testPoint, (0, 0, 255), 2)

    if mode == 1:
        solidBsp.draw(display)

    display.end()