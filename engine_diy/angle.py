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
        if self.deg < 0:
            self.deg += 360

    def __add__(self, d): # +
        return Angle(self.deg + d)
    def __iadd__(self, d): # +=
        self.deg += d
        self.normalize()
        return self

    def __sub__(self, d): # -
        return Angle(self.deg - d)
    def __isub__(self, d): # -=
        self.deg -= d
        self.normalize()
        return self
    def __neg__(self): # -a
        return Angle(360 - self.deg)

    def __mul__(self, d): # *
        return Angle(self.deg * d)
    def __imul__(self, d): # *=
        self.deg *= d
        self.normalize()
        return self

    def __truediv__(self, d): # /
        return Angle(self.deg / d)
    def __itruediv__(self, d): # /=
        self.deg /= d
        self.normalize()
        return self

    def __lt__(self, d): # <
        return self.deg < d
    def __le__(self, d): # <=
        return self.deg <= d

    def __gt__(self, d): # >
        return self.deg > d
    def __ge__(self, d): # >=
        return self.deg >= d

    def __str__(self):
        return "{}".format(self.deg)

    def toVector(self):
        rad = self.deg * math.pi / 180
        return math.cos(rad), math.sin(rad)

    def fromRadians(radians):
        return Angle(radians * 180 / math.pi)

