from enum import Enum

class Map(object):
    def __init__(self):
        self.name = ""
        self.vertices = []
        self.linedefs = []

class MapLumpsIndex:
    THINGS    = 1
    LINEDEFS  = 2
    SIDEDEFS  = 3
    VERTEXES  = 4
    SEAGS     = 5
    SSECTORS  = 6
    NODES     = 7
    SECTORS   = 8
    REJECT    = 9
    BLOCKMAP  = 10
    COUNT     = 11

class Vertex(object):
    def __init__(self):
        self.x = 0 # 2byte signed short
        self.y = 0 # 2byte signed short
    def __str__(self):
        return "{},{}".format(self.x, self.y)

class Linedef(object):
    def __init__(self):
        # all 2 bytes (14 bytes)
        self.startVertex = 0 # uint16
        self.endVertex = 0 # uint16
        self.flags = 0 # uint16
        self.lineType = 0 # uint16
        self.sectorTag = 0 # uint16
        self.frontSideDef = 0 # uint16
        self.backSideDef = 0 # uint16
    def __str__(self):
        return "s.{},e.{} f.{} t.{} s.{} f.{} b.{}"\
                .format(self.startVertex, self.endVertex,\
                self.flags, self.lineType, self.sectorTag,\
                self.frontSideDef, self.backSideDef)

class LinedefFlags:
    BLOCKING      = 0,
    BLOCKMONSTERS = 1,
    TWOSIDED      = 2,
    DONTPEGTOP    = 4,
    DONTPEGBOTTOM = 8,
    SECRET        = 16,
    SOUNDBLOCK    = 32,
    DONTDRAW      = 64,
    DRAW          = 128

