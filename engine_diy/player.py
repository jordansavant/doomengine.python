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
        spanAngle = v1Angle.subA(v2Angle)
        if spanAngle.gteF(180):
            return None

    def clipSegToFov(self, seg, fovd = 90):
        fov = Angle(fovd)
        v1 = map.vertices[seg.startVertexID]
        v2 = map.vertices[seg.endVertexID]
        return self.clipVerticesToFov(v1, v2, fov)

    def clipVerticesToFov(self, v1, v2, fovd = 90):
        fov = Angle(fovd)
        v1Angle = self.angleToVertex(v1)
        v2Angle = self.angleToVertex(v2)
        spanAngle = v1Angle.subA(v2Angle)
        if spanAngle.gteF(180):
            return None
        # Cases
        #  ~: Seg left and right are in fov and fully visible
        #  A: Seg is all the way to the left and not visible
        #  B: Seg is to the right and not visible
        #  C: Right part of seg is visible and left is clipped
        #  D: Left part of seg is visible and right is clipped
        #  E: Left and right are clipped but middle is visible
        # segs must be facing us
        # segs are made of two vertices
        # rotate the seg minus the player angle
        v1Angle = v1Angle.subA(self.angle)
        v2Angle = v2Angle.subA(self.angle)
        # this puts their vertices around the 0 degree
        # left side of FOV is 45
        # right side of FOV = -45 (315)
        # if we rotate player to 45 then
        # left side is at 90
        # right side is at 0 (no negative comparisons)
        # if V1 is > 90 its outside
        # if V2 is < 0 its outside
        # v1 test:
        halfFov = fov.divF(2)
        v1Moved = v1Angle.addA(halfFov)
        if v1Moved.gtA(fov):
            # v1 is outside the fov
            # check if angle of v1 to v2 is also outside fov
            # by comparing how far v1 is away from fov
            # if more than dist v1 to v2 then the angle outside fov
            v1MovedAngle = v1Moved.subA(fov)
            if v1MovedAngle.gteA(spanAngle):
                return None

            # v2 is valid, clip v1
            v1Angle = halfFov
        # v2 test: (we cant have angle < 0 so subtract angle from halffov)
        v2Moved = halfFov.subA(v2Angle)
        if v2Moved.gtA(fov):
            v2Angle = halfFov.neg()

        # rerotate angles
        v1Angle.iaddA(fov)
        v2Angle.iaddA(fov)

        return v1Angle, v2Angle

