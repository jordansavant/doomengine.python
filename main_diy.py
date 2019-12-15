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
game.setupWindow(1600, 1200)

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
    gh = (game.height - pad*2)
    scale = min(gw/map.width, gh/map.height)

    # center the map on the screen
    xoff = (game.width - (map.width * scale))/2 - (map.minx * scale)
    yoff = (game.height - (map.height *scale))/2 + (map.maxy * scale)

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

    # render things as dots
    for i, thing in enumerate(map.things):
        x = thing.x * scale + xoff
        y = -thing.y * scale + yoff # cartesian flip
        game.drawPoint([x,y], (1,0,0,0), 2)

    game.drawEnd()


    # dinky gameloop
    game.sleep()
