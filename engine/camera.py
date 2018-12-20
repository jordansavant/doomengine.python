import math

class Camera(object):

    def __init__(self):
        self.worldX = 0
        self.worldY = 0
        self.angle = 0

    def fncross(self, x1, y1, x2, y2):
        return x1 * y2 - y1 * x2

    def intersect(self, x1, y1, x2, y2, x3, y3, x4, y4):
        x = self.fncross(x1, y1, x2, y2)
        y = self.fncross(x3, y3, x4, y4)
        det = self.fncross(x1 - x2, y1 - y2, x3 - x4, y3 - y4)
        x = self.fncross(x, x1 - x2, y, x3 - x4) / det
        y = self.fncross(x, y1 - y2, y, y3 - y4) / det
        return (x, y)

    def transformWall(self, lineDef):

        # Transform vertices relative to player
        tx1 = lineDef.start[0] - self.worldX
        ty1 = lineDef.start[1] - self.worldY
        tx2 = lineDef.end[0] - self.worldX
        ty2 = lineDef.end[1] - self.worldY

        # Rotate them around the players view
        tz1 = tx1 * math.cos(self.angle) + ty1 * math.sin(self.angle)
        tz2 = tx2 * math.cos(self.angle) + ty2 * math.sin(self.angle)
        tx1 = tx1 * math.sin(self.angle) - ty1 * math.cos(self.angle)
        tx2 = tx2 * math.sin(self.angle) - ty2 * math.cos(self.angle)

        return (tx1, ty1, tz1, tx2, ty2, tz2)

    def projectWall(self, lineDef, surfaceWidth, surfaceHeight):

        halfW = surfaceWidth / 2
        halfH = surfaceHeight / 2

        # PROJECTED
        (tx1, ty1, tz1, tx2, ty2, tz2) = self.transformWall(lineDef)

        # PERSPECTIVE TRANSFORMED

        # Clip
        # determine clipping, if both z's < 0 its totally behind
        # if only 1 is negative it can be clipped
        if tz1 > 0 or tz2 > 0:
            # if line crosses the players view plane clip it
            ix1, iz1 = self.intersect(tx1, tz1, tx2, tz2, -0.0001, 0.0001, -20, 5)
            ix2, iz2 = self.intersect(tx1, tz1, tx2, tz2, 0.0001, 0.0001, 20, 5)
            if tz1 <= 0:
                if iz1 > 0:
                    tx1 = ix1
                    tz1 = iz1
                else:
                    tx1 = ix2
                    tz1 = iz2
            if tz2 <= 0:
                if iz1 > 0:
                    tx2 = ix1
                    tz2 = iz1
                else:
                    tx2 = ix2
                    tz2 = iz2

        # If not behind us
        if (tz1 > 0 and tz2 > 0):
            # Transform
            print(tx1, tz1)
            # 16 is effects FoV, the bigger the narrower
            # TODO: its either halfW or halfH, haven't figured it out, originally just "50"
            x1 = -tx1 * 16 / tz1
            y1a = -halfW / tz1
            y1b = halfW / tz1

            x2 = -tx2 * 16 / tz2
            y2a = -halfW / tz2
            y2b = halfW / tz2

            # get parts
            topLine = [[halfW + x1, halfH + y1a], [halfW + x2, halfH + y2a]]
            bottomLine = [[halfW + x1, halfH + y1b], [halfW + x2, halfH + y2b]]
            
            leftLine = [[halfW + x1, halfH + y1a], [halfW + x1, halfH + y1b]]
            rightLine = [[halfW + x2, halfH + y2a], [halfW + x2, halfH + y2b]]

            return (topLine, rightLine, bottomLine, leftLine)
        
        return (None, None, None, None)
