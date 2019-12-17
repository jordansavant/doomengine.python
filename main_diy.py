import sys, engine_diy
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
player.x = map.playerThing.x
player.y = map.playerThing.y
player.angle = map.playerThing.angle

# setup game
game = Game2D()
game.setupWindow(1600, 1200)

pl = Plot(map, game)

while True:

    game.events()
    if game.over:
        break;

    # update

    # draw
    game.drawStart()

    # loop over linedefs
    for i, ld in enumerate(map.linedefs):
        start = map.vertices[ld.startVertex]
        end = map.vertices[ld.endVertex]
        # map is in cartesian, flip to screen y
        sx, sy = pl.ot(start.x, start.y)
        ex, ey = pl.ot(end.x, end.y)
        # draw the line
        game.drawLine([sx, sy], [ex, ey], (1,1,1,1), 1)

    # render things as dots (things list does not contain player thing)
    for i, thing in enumerate(map.things):
        x, y = pl.ot(thing.x, thing.y)
        game.drawPoint([x,y], (1,0,0,1), 2)

    ## render player
    px, py = pl.ot(player.x, player.y)
    game.drawPoint([px,py], (0,1,0,1), 2)

    ## render last sector node
    node = map.getRootNode()
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

    game.drawEnd()


    # dinky gameloop
    game.sleep()

