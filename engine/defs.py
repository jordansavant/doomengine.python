# A polygon is a collection of lines, each line has a direction
# All lines should be connected, meaning one should start where the last one ends

class LineDef(object):
    def __init__(self):
        self.start = []
        self.end = []
        self.previousLineDef = None
        self.nextLineDef = None

    def asRoot(self, startX, startY, endX, endY):
        self.start = [startX, startY]
        self.end = [endX, endY]
    
    def asChild(self, preLineDef, endX, endY):
        self.start = [preLineDef.end[0], preLineDef.end[1]]
        self.end = [endX, endY]
        self.previousLineDef = preLineDef
    
    def asLeaf(self, preLineDef, rootLineDef):
        self.start = [preLineDef.end[0], preLineDef.end[1]]
        self.end = [rootLineDef.start[0], rootLineDef.start[1]]
        self.previousLineDef = preLineDef

        