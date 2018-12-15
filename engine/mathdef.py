def crossProductLine(a, b):
    return a[0] * b[1] - a[1] * b[0]
    #{   return (p.x*q.y - p.y*q.x); }

def pointBehindSegment(point, a, b):
    cross = (b[0] - a[0]) * (point[1] - a[1]) - (b[1] - a[1]) * (point[0] - a[0])
    return cross > 0