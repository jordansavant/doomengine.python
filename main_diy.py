import sys, engine_diy
from engine_diy.wad import WAD


# path to wad
if len(sys.argv) - 1 > 0:
    path = sys.argv[1]
else:
    path = "wads/DOOM.WAD"


wad = WAD(path)
print(wad.info())

