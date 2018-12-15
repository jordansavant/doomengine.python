from engine.mathdef import crossProductLine
from engine.mathdef import normalize

# A polygon is a collection of lines, each line has a direction
# All lines should be connected, meaning one should start where the last one ends

class LineDef(object):
    def __init__(self):
        self.start = []
        self.end = []
        self.normal = None
        self.previousLineDef = None
        self.nextLineDef = None
        self.cross = None
        self.mid = []
        self.dir = []
        self.normals = []
        # TODO: get normals and stuff calculated here

    def asRoot(self, startX, startY, endX, endY):
        self.start = [startX, startY]
        self.end = [endX, endY]
        self.setup()
    
    def asChild(self, preLineDef, endX, endY):
        self.start = [preLineDef.end[0], preLineDef.end[1]]
        self.end = [endX, endY]
        self.previousLineDef = preLineDef
        self.setup()
    
    def asLeaf(self, preLineDef, rootLineDef):
        self.start = [preLineDef.end[0], preLineDef.end[1]]
        self.end = [rootLineDef.start[0], rootLineDef.start[1]]
        self.previousLineDef = preLineDef
        self.setup()

    def setup(self):
        self.setMid()
        self.setCross()
        self.setDir()
        self.setNormals()

    def setCross(self):
        self.cross = crossProductLine(self.start, self.end)

    def setMid(self):
        # (a.x+b.x)/2,(a.y+b.y)/2
        self.mid.append((self.start[0] + self.end[0]) / 2)
        self.mid.append((self.start[1] + self.end[1]) / 2)

    def setDir(self):
        # -(b.y-a.y),(b.x-a.x)
        self.dir.append(-(self.end[1] - self.start[1]))
        self.dir.append(self.end[0] - self.start[0])
    
    def setNormals(self):
        dx = self.end[0] - self.start[0]
        dy = self.end[1] - self.start[1]
        self.normals.append(normalize(-dy, dx)) # First normal is the one facing in (since we are Clockwise)
        self.normals.append(normalize(dy, -dx)) # Second normal is the one facing out (since we are Clockwise)

    def getFace(self):
        return
        # a connected polygon is a series of vertices, connected as lines
        # as they form the polygon, there is the "solid" interior and
        # the "empty" exterior
        # can we determine the outward face of a line knowing its start
        # and end?

