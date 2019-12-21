import math
from engine_diy.angle import Angle
from engine_diy.map import Vertex

class Player(object):
    def __init__(self):
        self.id = 0 # int32
        self.x = 0 # int32
        self.y = 0 # int32
        self.angle = 0 # int32

    def angleToVertex(self, vertex):
        vdx = vertex.x - self.x
        vdy = vertex.y - self.y

        radians = math.atan2(vdy, vdx)
        return Angle.fromRadians(radians)


