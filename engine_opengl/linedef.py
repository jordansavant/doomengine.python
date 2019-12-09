import random
from engine_opengl.mathdef import *

# A polygon is a collection of lines, each line has a direction
# All lines should be connected, meaning one should start where the last one ends

class LineDef(object):
    def __init__(self):
        self.start = []
        self.end = []
        self.facing = None
        self.mid = []
        self.normals = []
        self.drawColor = (random.randint(10, 255), random.randint(10, 255), random.randint(50, 255))
        self.height = 0
        self.isroot = False
        # TODO: get normals and stuff calculated here

    def asRoot(self, startX, startZ, endX, endZ, facing, height):
        self.start = [startX, startZ]
        self.end = [endX, endZ]
        self.facing = facing
        self.height = height
        self.isroot = True
        self.setup()

    def asChild(self, preLineDef, endX, endZ, facing, height):
        self.start = [preLineDef.end[0], preLineDef.end[1]]
        self.end = [endX, endZ]
        self.facing = facing
        self.height = height
        self.setup()

    def asLeaf(self, preLineDef, rootLineDef, facing, height):
        self.start = [preLineDef.end[0], preLineDef.end[1]]
        self.end = [rootLineDef.start[0], rootLineDef.start[1]]
        self.facing = facing
        self.height = height
        self.setup()

    def setup(self):
        self.setMidpoint()
        self.setNormals()

    def setMidpoint(self):
        # (a.x+b.x)/2,(a.y+b.y)/2
        self.mid.append((self.start[0] + self.end[0]) / 2)
        self.mid.append((self.start[1] + self.end[1]) / 2)

    def setNormals(self):
        dx = self.end[0] - self.start[0]
        dy = self.end[1] - self.start[1]
        self.normals.append(normalize(-dy, dx)) # First normal is the one facing in (if we are Clockwise)
        self.normals.append(normalize(dy, -dx)) # Second normal is the one facing out (if we are Clockwise)

    def isPointBehind(self, x, z):
        # If it is behind and we are facing left CW
        beh = pointBehindSegment([x, z], self.start, self.end) # true, false or none (for on the same plane)
        if beh != None:
            if self.facing == 1:
                return beh
            return not beh
        return None

    def classifyLine(self, testLine):
        # 1 = back
        # 2 = front
        # 3 = spanning
        # 4 = co planar
        points = [testLine.start, testLine.end]
        backCounter = 0
        frontCounter = 0
        for point in points:
            result = self.isPointBehind(point[0], point[1])
            if result == True:
                backCounter += 1
            if result == False:
                frontCounter +=1
            # if result == None:
                # co planar, no counters

        # spanning
        if backCounter != 0 and frontCounter != 0:
            return 3
        # back
        if backCounter:
            return 1
        # front
        if frontCounter:
            return 2
        return 4

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
        return intersection2d(self.start, self.end, other.start, other.end)

    def __str__(self):
        return "[{}->{}:{}:{}:{}]".format(self.start, self.end, self.height, self.facing, self.isroot)
