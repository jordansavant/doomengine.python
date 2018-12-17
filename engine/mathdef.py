import math

def crossProductLine(a, b):
    return a[0] * b[1] - a[1] * b[0]
    #{   return (p.x*q.y - p.y*q.x); }

def pointBehindSegment(point, a, b):
    cross = (b[0] - a[0]) * (point[1] - a[1]) - (b[1] - a[1]) * (point[0] - a[0])
    if cross > 0:
        return True
    if cross < 0:
        return False
    if cross == 0:
        return None

def normalize(a, b):
    if a != 0 or b != 0:
        length = math.sqrt(a * a + b * b)
        return [a / length, b / length]
    return [a, b]

def perp2d(a, b):
    return [-b, a]

def rotate2d(x, y, rads):
    cos = math.cos(rads)
    sin = math.sin(rads)

    return [(x * cos) - (y * sin), (x * sin) + (y * cos)]

def distance2d(x1, y1, x2, y2):
    x = x1 - x2
    y = y1 - y2
    return math.sqrt(x*x  + y*y)
