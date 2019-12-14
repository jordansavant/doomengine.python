import sys, engine_diy
from engine_diy.wad_loader import WADLoader


# path to wad
if len(sys.argv) - 1 > 0:
    path = sys.argv[1]
else:
    path = "wads/DOOM.WAD"


wadl = WADLoader(path)
print(wadl)

