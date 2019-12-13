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

def rad2deg(rad):
    return rad * 180 / math.pi

def deg2rad(deg):
    return deg * math.pi / 180

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

def toRadians(x, y):
    v = normalize(x, y)
    return math.atan2(v[1], v[0])

def toVector(rads):
    return [math.cos(rads), math.sin(rads)]

def intersection2d(splitterStart, splitterEnd, lineStart, lineEnd):
    s1 = splitterStart
    e1 = splitterEnd
    s2 = lineStart
    e2 = lineEnd

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
