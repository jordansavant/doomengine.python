import sys, engine_diy
from engine_diy.wad import WAD
from engine_diy.game2d import Game2D


# path to wad
if len(sys.argv) - 1 > 0:
    path = sys.argv[1]
else:
    path = "wads/DOOM.WAD"

# load WAD
wad = WAD(path)

# choose a map
map = wad.loadMap("E1M1")

# render map

game = Game2D()
game.setupWindow(1280, 720)

while True:

    game.events()
    if game.over:
        break;

    # update

    # draw
    game.drawStart()

    # loop over linedefs
    game.drawLine([100, 100], [200, 200], (1,1,1,1), 2)

    game.drawEnd()


    # dinky gameloop
    game.sleep()
