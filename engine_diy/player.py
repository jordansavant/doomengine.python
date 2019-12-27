import math
from engine_diy.angle import Angle
from engine_diy.map import *

class Player(object):
    def __init__(self):
        self.id = 0 # int32
        self.x = 0 # int32
        self.y = 0 # int32
        self.z = 0 # TODO needs to be set from floor he's on
        self.eyeHeight = 41 # from doom engine
        self.angle = Angle(0) # Angle object

        self.currentSector = None

    def setPosition(self, x, y):
        self.x = x
        self.y = y

    def setAngle(self, deg):
        self.angle = Angle(deg)

    def setSector(self, sector):
        self.currentSector = sector
        self.z = sector.floorHeight

    def getEyeZ(self):
        return self.z + self.eyeHeight

    def distanceToVertex(self, vertex):
        return math.sqrt((self.x - vertex.x) ** 2 + (self.y - vertex.y) ** 2)

    def angleToVertex(self, vertex):
        vdx = vertex.x - self.x
        vdy = vertex.y - self.y

        radians = math.atan2(vdy, vdx)
        return Angle.fromRadians(radians)

    def isSegFacingUs(self, seg):
        # if angle to vertex1 > vertex2
        # then the seg is facing us
        # this is because the placement of a seg
        # vertices indicate which way it faces
        v1 = map.vertices[seg.startVertexID]
        v2 = map.vertices[seg.endVertexID]
        v1Angle = self.angleToVertex(v1)
        v2Angle = self.angleToVertex(v2)
        spanAngle = v1Angle.subA(v2Angle)
        if spanAngle.gteF(180):
            return None


