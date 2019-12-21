import math
from engine_diy.angle import Angle
from engine_diy.map import *

class Player(object):
    def __init__(self):
        self.id = 0 # int32
        self.x = 0 # int32
        self.y = 0 # int32
        self.angle = Angle(0) # Angle object

    def setPosition(self, x, y):
        self.x = x
        self.y = y

    def setAngle(self, deg):
        self.angle = Angle(deg)

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
        spanAngle = v1Angle - v2Angle # operator overloaded
        if spanAngle >= 180: # operator overloaded
            return False

