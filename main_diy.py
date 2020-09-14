import sys, engine_diy, pygame, random, math
from engine_diy.wad import WAD
from engine_diy.game2d import Game2D
from engine_diy.map import *
from engine_diy.player import Player
from engine_diy.angle import Angle
from engine_diy.segment_range import *
from engine_diy.fps_renderer import FpsRenderer


#############
## HELPERS ##
#############
#############

class Plot(object):
    def __init__(self, map, surfWidth, surfHeight):
        # calculate map scale to fit screen minus padding
        self.pad = pad = 10
        gw = (surfWidth - self.pad*2)
        gh = (surfHeight - self.pad*2)
        self.scale = scale = min(gw/map.width, gh/map.height)

        # center the map on the screen
        self.xoff = (surfWidth - (map.width * scale))/2 - (map.minx * scale)
        self.yoff = (surfHeight - (map.height *scale))/2 + (map.maxy * scale)
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

# helper method to highlight a single subsector
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

def drawPlayer(game, pl, player, rgba=(0,1,0,1)):
    px, py = pl.ot(player.x, player.y)
    # player pointer
    dirx, diry = player.angle.toVector()
    endx, endy = pl.ot(player.x + dirx*40, player.y + diry*40)
    game.drawLine([px, py], [endx, endy], rgba, 1)
    # player dot
    game.drawRectangle([px-2,py-2], 4, 4, rgba)


#############
##  START  ##
#############
#############

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
game.setupWindow(1280, 720)

# main screen plot
pl = Plot(map, game.width, game.height)

# fps window
fov = 90
fpsWinWidth = 480 # 320
fpsWinHeight = 300 # 200
fpsWinOffX = 20
fpsWinOffY = 20
fpsRenderer = FpsRenderer(map, player, game, fov, fpsWinWidth, fpsWinHeight, fpsWinOffX, fpsWinOffY)

# render helpers
mode = 13 # polygon version
max_modes = 15
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
    player.angle.iaddF(5) # rotate left
game.onKeyHold(pygame.K_LEFT, on_left)
def on_right():
    global player
    player.angle.isubF(5) # rotate right
game.onKeyHold(pygame.K_RIGHT, on_right)
def on_w():
    global player
    player.x += player.angle.getCos() * 5
    player.y += player.angle.getSin() * 5
game.onKeyHold(pygame.K_w, on_w)
def on_s():
    global player
    player.x -= player.angle.getCos() * 5
    player.y -= player.angle.getSin() * 5
game.onKeyHold(pygame.K_s, on_s)
def on_a():
    global player
    player.x += player.angle.addF(90).getCos() * 5
    player.y += player.angle.addF(90).getSin() * 5
game.onKeyHold(pygame.K_a, on_a)
def on_d():
    global player
    player.x -= player.angle.addF(90).getCos() * 5
    player.y -= player.angle.addF(90).getSin() * 5
game.onKeyHold(pygame.K_d, on_d)
def on_z():
    global player
    player.z -= 5
game.onKeyHold(pygame.K_z, on_z)
def on_x():
    global player
    player.z += 5
game.onKeyHold(pygame.K_x, on_x)
def on_space():
    global player
    player.x = 1291
    player.y = -3011
game.onKeyUp(pygame.K_SPACE, on_space)


###############
## GAME LOOP ##
###############
###############

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

    # MODE LOOPS
    game.setFPS(60)

    # RENDER THINGS AS DOTS
    if mode == 1:
        for i, thing in enumerate(map.things):
            x, y = pl.ot(thing.x, thing.y)
            game.drawRectangle([x-2,y-2], 4, 4, (1,0,0,1))

        ## render player
        px, py = pl.ot(player.x, player.y)
        game.drawRectangle([px-2,py-2], 4, 4, (0,1,0,1))

    # RENDER ROOT NODE BSP BOXES
    if mode == 2:
        drawNode(game, map.getRootNode())

    # RENDER ALL NODE BSP BOXES
    if mode == 3:
        for i, n in enumerate(map.nodes):
            drawNode(game, n)

    # RENDER SUBSECTORS VIA BSP TRAVERSAL
    if mode == 4:
        game.setFPS(10)
        modeSSrenderIndex = ( modeSSrenderIndex + 1 ) % len(map.subsectors)
        drawSubsector(modeSSrenderIndex, (1, 0, 0, 1))

    # RENDER SUBSECTOR OF PLAYER
    if mode == 5:
        # render player
        px, py = pl.ot(player.x, player.y)
        game.drawRectangle([px-2,py-2], 4, 4, (0,1,0,1))
        # render player subsector
        ss = map.getSubsectorAtPosition(player.x, player.y)
        drawSubsector(ss.ID)

    # RENDER ANGLE FROM PLAYER TO EACH VERTEX
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

    # RENDER FPS FOR WALL EDGES ONLY
    if mode == 7 or mode == 8:
        # render player
        drawPlayer(game, pl, player)

        # render only the wall edges
        def onSegInspect(seg, v1, v2):
            # render the seg (helper)
            v1x, v1y = pl.ot(v1.x, v1.y)
            v2x, v2y = pl.ot(v2.x, v2.y)
            game.drawLine([v1x,v1y], [v2x,v2y], (1,0,0,1), 2)

        fpsRenderer.edges_render(mode == 8, onSegInspect)

    # RENDER FPS WITH WALL CULLING ONLY
    if mode == 9:
        # render player
        drawPlayer(game, pl, player)

        # test rendering segs with wall culling
        def onSegInspect(seg, v1, v2):
            # render the seg (helper)
            v1x, v1y = pl.ot(v1.x, v1.y)
            v2x, v2y = pl.ot(v2.x, v2.y)
            game.drawLine([v1x,v1y], [v2x,v2y], (1,0,0,1), 2)

        fpsRenderer.wallcull_render(onSegInspect)

    # RENDER FPS WITH WOLFENSTEIN WALLS
    if mode == 10:
        # render player
        drawPlayer(game, pl, player)

        # test rendering segs with wall culling
        def onSegInspect(seg, v1, v2):
            # render the seg (helper)
            v1x, v1y = pl.ot(v1.x, v1.y)
            v2x, v2y = pl.ot(v2.x, v2.y)
            game.drawLine([v1x,v1y], [v2x,v2y], (1,0,0,1), 2)

        fpsRenderer.wolfenstein_render(onSegInspect)

    # RENDER FPS WITH COLORED DOOM SOLID WALLS
    if mode == 11:
        # render player
        drawPlayer(game, pl, player)

        # test rendering segs with wall culling
        def onSegInspect(seg, v1, v2):
            # render the seg (helper)
            v1x, v1y = pl.ot(v1.x, v1.y)
            v2x, v2y = pl.ot(v2.x, v2.y)
            game.drawLine([v1x,v1y], [v2x,v2y], (1,0,0,1), 2)

        fpsRenderer.doomsolids_render(onSegInspect)

    # RENDER FPS WITH COLORED DOOM SOLID AND PARTIAL WALLS
    if mode == 12:
        # render player
        drawPlayer(game, pl, player)

        # test rendering segs with wall culling
        def onSegInspect(seg, v1, v2):
            # render the seg (helper)
            v1x, v1y = pl.ot(v1.x, v1.y)
            v2x, v2y = pl.ot(v2.x, v2.y)
            game.drawLine([v1x,v1y], [v2x,v2y], (1,0,0,1), 2)

        fpsRenderer.doomportals_render(onSegInspect)

    # RENDER FPS WITH SOLID,PARTIAL AND STORED WALLS
    if mode == 13 or mode == 14:
        # Also sets player to sector floor
        playerSector = map.getSectorAtPosition(player.x, player.y)
        player.setSector(playerSector)

        # render player
        drawPlayer(game, pl, player)

        lineMode = mode == 14
        fpsRenderer.doomhistory_render(lineMode)

    game.drawEnd()


    # dinky gameloop
    game.sleep()

