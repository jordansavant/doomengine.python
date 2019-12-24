import math

# class is built to support a
# 360 degree angle system and
# ensures an angle is always
# between 0 and 359

# DOOM used a BAM Binary Angular
# Measurement which I believe
# just used Integers scaled very
# high to represent floating point
# values if the floating point
# range was actually low, such
# as 0 - 360

class Angle(object):

    def __init__(self, deg):
        self.deg = deg
        self.normalize()

    def normalize(self):
        self.deg = self.deg % 360
        while self.deg < 0:
            self.deg += 360

    # addition
    def addF(self, d):
        return Angle(self.deg + d)
    def iaddF(self, d):
        self.deg += d
        self.normalize()
        return self
    def addA(self, a):
        return self.addF(a.deg)
    def iaddA(self, a):
        return self.iaddF(a.deg)

    # subtraction
    def subF(self, d):
        return Angle(self.deg - d)
    def isubF(self, d):
        self.deg -= d
        self.normalize()
        return self
    def subA(self, a):
        return self.subF(a.deg)
    def isubA(self, a):
        return self.isubF(a.deg)

    # negate
    def neg(self):
        return Angle(360 - self.deg)

    # multiplication
    def mulF(self, d):
        return Angle(self.deg * d)
    def imulF(self, d):
        self.deg *= d
        self.normalize()
        return self
    def mulA(self, a):
        return self.mulF(a.deg)
    def imulA(self, a):
        return self.imulF(a.deg)

    # division
    def divF(self, d): # /
        return Angle(self.deg / d)
    def idivF(self, d): # /=
        self.deg /= d
        self.normalize()
        return self
    def divA(self, a):
        return self.divF(a.deg)
    def idivA(self, a):
        return self.idivF(a.deg)

    # comparison
    def ltF(self, d): # <
        return self.deg < d
    def lteF(self, d): # <=
        return self.deg <= d
    def ltA(self, a):
        return self.ltF(a.deg)
    def lteA(self, a):
        return self.lteF(a.deg)

    def gtF(self, d): # >
        return self.deg > d
    def gteF(self, d): # >=
        return self.deg >= d
    def gtA(self, a):
        return self.gtF(a.deg)
    def gteA(self, a):
        return self.gteF(a.deg)

    def __str__(self):
        return "A:{}".format(self.deg)

    def getCos(self):
        return math.cos(self.toRadians())
    def getSin(self):
        return math.sin(self.toRadians())
    def getTan(self):
        return math.tan(self.toRadians())
    def getSigned(self):
        if self.deg > 180:
            return self.deg - 360
        return self.deg

    def new(self):
        return Angle(self.deg)

    def toVector(self):
        rad = self.deg * math.pi / 180
        return math.cos(rad), math.sin(rad)
    def toRadians(self):
        return self.deg * math.pi / 180

    def fromRadians(radians):
        return Angle(radians * 180 / math.pi)

