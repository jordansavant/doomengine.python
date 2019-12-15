import sys, engine_diy
from engine_diy.wad import WAD
from engine_diy.game2d import Game2D


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

# setup game
game = Game2D()
game.setupWindow(1024, 768)

while True:

    game.events()
    if game.over:
        break;

    # update

    # draw
    game.drawStart()

    # calculate map scale to fit screen minus padding
    pad = 10
    gw = (game.width - pad*2)
    mw = map.maxx - map.minx
    gh = (game.height - pad*2)
    mh = map.maxy - map.miny
    scaleX = gw/mw
    scaleY = gh/mh
    scale = min(scaleX, scaleY)

    # center the map on the screen
    xoff = (game.width - (mw * scale))/2 - (map.minx * scale)
    yoff = (game.height - (mh *scale))/2 + (map.maxy * scale)

    # loop over linedefs
    for i, ld in enumerate(map.linedefs):
        start = map.vertices[ld.startVertex]
        end = map.vertices[ld.endVertex]
        # map is in cartesian, flip to screen y
        sx = start.x * scale + xoff
        sy = -start.y * scale + yoff
        ex = end.x * scale + xoff
        ey = -end.y * scale + yoff
        # draw the line
        game.drawLine([sx, sy], [ex, ey], (1,1,1,1), 1)

    game.drawEnd()


    # dinky gameloop
    game.sleep()
