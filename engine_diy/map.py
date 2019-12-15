from enum import Enum

class Map(object):
    def __init__(self):
        self.name = ""
        self.vertices = []
        self.linedefs = []
        self.minx = None
        self.maxx = None
        self.miny = None
        self.maxy = None
        self.width = None
        self.height = None
    # helper method to get min and
    # max values of the maps coords
    def calcMinMax(self):
        for i, ld in enumerate(self.linedefs):
            start = self.vertices[ld.startVertex]
            end = self.vertices[ld.endVertex]

            if self.minx == None or self.minx > start.x:
                self.minx = start.x
            if self.maxx == None or self.maxx < start.x:
                self.maxx = start.x
            if self.minx == None or self.minx > end.x:
                self.minx = end.x
            if self.maxx == None or self.maxx < end.x:
                self.maxx = end.x

            if self.miny == None or self.miny > start.y:
                self.miny = start.y
            if self.maxy == None or self.maxy < start.y:
                self.maxy = start.y
            if self.miny == None or self.miny > end.y:
                self.miny = end.y
            if self.maxy == None or self.maxy < end.y:
                self.maxy = end.y
        self.width = self.maxx - self.minx
        self.height = self.maxy - self.miny

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

