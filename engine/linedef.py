import random
from engine.mathdef import crossProductLine
from engine.mathdef import normalize
from engine.mathdef import pointBehindSegment

# A polygon is a collection of lines, each line has a direction
# All lines should be connected, meaning one should start where the last one ends

class LineDef(object):
    def __init__(self):
        self.start = []
        self.end = []
        self.normal = None
        self.cross = None
        self.facing = None
        self.mid = []
        self.dir = []
        self.normals = []
        self.drawColor = (random.randint(10, 255), random.randint(10, 255), random.randint(50, 255))
        # TODO: get normals and stuff calculated here

    def asRoot(self, startX, startY, endX, endY, facing):
        self.start = [startX, startY]
        self.end = [endX, endY]
        self.facing = facing
        self.setup()
    
    def asChild(self, preLineDef, endX, endY, facing):
        self.start = [preLineDef.end[0], preLineDef.end[1]]
        self.end = [endX, endY]
        self.facing = facing
        self.setup()
    
    def asLeaf(self, preLineDef, rootLineDef, facing):
        self.start = [preLineDef.end[0], preLineDef.end[1]]
        self.end = [rootLineDef.start[0], rootLineDef.start[1]]
        self.facing = facing
        self.setup()

    def setup(self):
        self.setMid()
        self.setCross()
        self.setDir()
        self.setNormals()

    def setCross(self):
        # TODO: unused
        self.cross = crossProductLine(self.start, self.end)

    def setMid(self):
        # (a.x+b.x)/2,(a.y+b.y)/2
        self.mid.append((self.start[0] + self.end[0]) / 2)
        self.mid.append((self.start[1] + self.end[1]) / 2)

    def setDir(self):
        # TODO: unused
        # -(b.y-a.y),(b.x-a.x)
        self.dir.append(self.end[0] - self.start[0])
        self.dir.append(-(self.end[1] - self.start[1]))
    
    def setNormals(self):
        dx = self.end[0] - self.start[0]
        dy = self.end[1] - self.start[1]
        self.normals.append(normalize(-dy, dx)) # First normal is the one facing in (if we are Clockwise)
        self.normals.append(normalize(dy, -dx)) # Second normal is the one facing out (if we are Clockwise)

    def isPointBehind(self, a, b):
        # If it is behind and we are facing left CW
        return pointBehindSegment([a, b], self.start, self.end) and self.facing == 1

    def classifyLine(self, testLine):
        points = [testLine.start, testLine.end]
        backCounter = 0
        frontCounter = 0
        for point in points:
            if self.isPointBehind(point[0], point[1]):
                backCounter += 1
            else:
                frontCounter +=1
        # spanning
        if backCounter != 0 and frontCounter != 0:
            return 3
        # back
        if backCounter:
            return 1
        # front
        if frontCounter:
            return 2

        # 1 = back
        # 2 = front
        # 3 = spanning
        # 4 = co planar TODO our math is not checking for 0
        return 1

    def split(self, other):
        # get the intersecting point
        intersection = self.findIntersection(other)
        if intersection:
            # create a line from other start to intersection and return that as front??
            splitA = [other.start, intersection]
            splitB = [intersection, other.end]
            aBehind = self.isPointBehind(other.start[0], other.start[1])
            # return them with position 0 behind and position 1 in front
            if aBehind:
                return [splitA, splitB]
            else:
                return [splitB, splitA]
        return None

    def findIntersection(self, other):
        s1 = self.start
        e1 = self.end
        s2 = other.start
        e2 = other.end

        a1 = e1[1] - s1[1]
        b1 = s1[0] - e1[0]
        c1 = a1 * s1[0] + b1 * s1[1]
 
        a2 = e2[1] - s2[1]
        b2 = s2[0] - e2[0]
        c2 = a2 * s2[0] + b2 * s2[1]
 
        delta = a1 * b2 - a2 * b1
        # if lines are parallel, the result will be delta = 0
        if delta != 0:
            return [(b2 * c1 - b1 * c2) / delta, (a1 * c2 - a2 * c1) / delta]
        return None


