import sys, engine_diy, pygame, random
from engine_diy.wad import WAD
from engine_diy.game2d import Game2D
from engine_diy.map import *
from engine_diy.player import Player

class Plot(object):
    def __init__(self, map, game):
        # calculate map scale to fit screen minus padding
        self.pad = pad = 10
        gw = (game.width - self.pad*2)
        gh = (game.height - self.pad*2)
        self.scale = scale = min(gw/map.width, gh/map.height)

        # center the map on the screen
        self.xoff = (game.width - (map.width * scale))/2 - (map.minx * scale)
        self.yoff = (game.height - (map.height *scale))/2 + (map.maxy * scale)
    def ot(self, x, y):
        # flip cartesian, scale and translate
        x = x * self.scale + self.xoff
        y = -y * self.scale + self.yoff
        return x, y

# helper method to draw map nodes
def drawNode(game, node):
    ## draw front box
    rgba = (0, 1, 0, .5)
    fl, ft = pl.ot(node.frontBoxLeft, node.frontBoxTop)
    fr, fb = pl.ot(node.frontBoxRight, node.frontBoxBottom)
    game.drawBox([fl, ft], [fr, ft], [fr, fb], [fl, fb], rgba, 2)

    ## draw back box
    rgba = (1, 0, 0, .5)
    bl, bt = pl.ot(node.backBoxLeft, node.backBoxTop)
    br, bb = pl.ot(node.backBoxRight, node.backBoxBottom)
    game.drawBox([bl, bt], [br, bt], [br, bb], [bl, bb], rgba, 2)

    ## draw the node seg splitterd
    rgba = (1, 1, 0, 1)
    xp, yp = pl.ot(node.xPartition, node.yPartition)
    xc, yc = pl.ot(node.xPartition + node.xChangePartition, node.yPartition + node.yChangePartition)
    game.drawLine([xp, yp], [xc, yc], (0,0,1,1), 3)

def drawSubsector(subsectorId, rgba=None):
    global game, map, pl
    subsector = map.subsectors[subsectorId]
    if rgba is None:
        rgba = (random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), 1)
    for i in range(0, subsector.segCount):
        seg = map.segs[subsector.firstSegID + i]
        startVertex = map.vertices[seg.startVertexID]
        endVertex = map.vertices[seg.endVertexID]
        sx, sy = pl.ot(startVertex.x, startVertex.y)
        ex, ey = pl.ot(endVertex.x, endVertex.y)
        game.drawLine([sx,sy], [ex,ey], rgba, 2)

# path to wad
if len(sys.argv) > 1:
    path = sys.argv[1]
else:
    path = "wads/DOOM.WAD"
# map name
if len(sys.argv) > 2:
    mapname = sys.argv[2]
else:
    mapname = "E1M1"

# load WAD
wad = WAD(path)

# choose a map
map = wad.loadMap(mapname)
if map == None:
    print("ERROR: invalid map {}".format(mapname))
    quit()

# build player
player = Player()
player.id = 1
player.setPosition(map.playerThing.x, map.playerThing.y)
player.setAngle(map.playerThing.angle)


# setup game
game = Game2D()
game.setupWindow(1600, 1200)

pl = Plot(map, game)

# render helpers
mode = 0
max_modes = 8
def mode_up():
    global mode
    mode = (mode + 1) % max_modes
game.onKeyUp(pygame.K_UP, mode_up)
def mode_down():
    global mode
    mode = (mode - 1) % max_modes
game.onKeyUp(pygame.K_DOWN, mode_down)
def on_left():
    global player
    player.angle.iaddF(2) # rotate left
game.onKeyHold(pygame.K_LEFT, on_left)
def on_right():
    global player
    player.angle.isubF(2) # rotate right
game.onKeyHold(pygame.K_RIGHT, on_right)
def on_w():
    global player
    player.y += 5 # move "up"/"forward" (positive y in game world)
game.onKeyHold(pygame.K_w, on_w)
def on_s():
    global player
    player.y -= 5 # move "down"/"backward" (negative y in game world)
game.onKeyHold(pygame.K_s, on_s)
def on_a():
    global player
    player.x -= 5 # move "left"
game.onKeyHold(pygame.K_a, on_a)
def on_d():
    global player
    player.x += 5 # move "left"
game.onKeyHold(pygame.K_d, on_d)

modeSSrenderIndex = 0
modeAngleIndex = 0
while True:

    game.events()
    if game.over:
        break;

    # update

    # draw
    game.drawStart()

    # loop over linedefs
    for i, ld in enumerate(map.linedefs):
        start = map.vertices[ld.startVertexID]
        end = map.vertices[ld.endVertexID]
        # map is in cartesian, flip to screen y
        sx, sy = pl.ot(start.x, start.y)
        ex, ey = pl.ot(end.x, end.y)
        # draw the line
        game.drawLine([sx, sy], [ex, ey], (1,1,1,1), 1)

    game.setFPS(60)
    # render things as dots (things list does not contain player thing)
    if mode == 1:
        for i, thing in enumerate(map.things):
            x, y = pl.ot(thing.x, thing.y)
            game.drawRectangle([x-2,y-2], 4, 4, (1,0,0,1))

        ## render player
        px, py = pl.ot(player.x, player.y)
        game.drawRectangle([px-2,py-2], 4, 4, (0,1,0,1))
    if mode == 2:
        drawNode(game, map.getRootNode())
    if mode == 3:
        for i, n in enumerate(map.nodes):
            drawNode(game, n)
    if mode == 4:
        game.setFPS(10)
        modeSSrenderIndex = ( modeSSrenderIndex + 1 ) % len(map.subsectors)
        drawSubsector(modeSSrenderIndex, (1, 0, 0, 1))
    if mode == 5:
        # render player
        px, py = pl.ot(player.x, player.y)
        game.drawRectangle([px-2,py-2], 4, 4, (0,1,0,1))
        # render player subsector
        ssId = map.getSubsector(player.x, player.y)
        drawSubsector(ssId)
    if mode == 6:
        game.setFPS(10)
        modeAngleIndex = (modeAngleIndex + 1) % len(map.vertices)
        # render player
        px, py = pl.ot(player.x, player.y)
        game.drawRectangle([px-2,py-2], 4, 4, (0,1,0,1))
        # render target vertex
        vertex = map.vertices[modeAngleIndex]
        vx, vy = pl.ot(vertex.x, vertex.y)
        game.drawRectangle([vx-3,vy-3], 6, 6, (1,0,0,1))
        # test angle
        a = player.angleToVertex(vertex)
        dirx, diry = a.toVector()
        # render angle
        endx, endy = pl.ot(player.x + dirx*50, player.y + diry*50)
        game.drawLine([px, py], [endx, endy], (0,1,1,1), 2)
    if mode == 7:
        # test segs that are in 90deg FOV of player
        # render player
        px, py = pl.ot(player.x, player.y)
        game.drawRectangle([px-2,py-2], 4, 4, (0,1,0,1))
        # iterate all of the segs and test them, if they have angles render seg
        for i, seg in enumerate(map.segs):
            v1 = map.vertices[seg.startVertexID]
            v2 = map.vertices[seg.endVertexID]
            angles = player.clipVerticesToFov(v1, v2, 90)
            if angles is not None:
                # render the seg
                v1x, v1y = pl.ot(v1.x, v1.y)
                v2x, v2y = pl.ot(v2.x, v2.y)
                game.drawLine([v1x,v1y], [v2x,v2y], (1,0,0,1), 2)

    game.drawEnd()


    # dinky gameloop
    game.sleep()

