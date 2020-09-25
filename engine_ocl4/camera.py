import math

class Camera(object):

    def __init__(self):
        self.worldX = 0
        self.worldY = 0
        self.worldZ = 0 # floor + camera height
        self.angle = 0
        self.hfov = .73 # multiply by screen height
        self.vfov = .2 # multiply by screen height

    def __str__(self):
        return "{},{}".format((int)(self.worldX), (int)(self.worldY))

    def fncross(self, x1, y1, x2, y2):
        return x1 * y2 - x2 * y1

    def intersect(self, x1, y1, x2, y2, x3, y3, x4, y4):
        x = self.fncross(self.fncross(x1,y1, x2,y2), (x1)-(x2), self.fncross(x3,y3, x4,y4), (x3)-(x4)) / self.fncross((x1)-(x2), (y1)-(y2), (x3)-(x4), (y3)-(y4))
        y = self.fncross(self.fncross(x1,y1, x2,y2), (y1)-(y2), self.fncross(x3,y3, x4,y4), (y3)-(y4)) / self.fncross((x1)-(x2), (y1)-(y2), (x3)-(x4), (y3)-(y4))
        return (x, y)

    def transformWall(self, lineDef, debug = False):

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

    def yaw(self, y, z):
        return y + z * self.angle
        # Yaw(y,z) (y + z*player.yaw)

    def projectWall(self, lineDef, surfaceWidth, surfaceHeight, debug = False):

        lhfov = self.hfov * surfaceHeight
        lvfov = self.vfov * surfaceHeight

        halfW = surfaceWidth / 2
        halfH = surfaceHeight / 2

        # PROJECTED
        (tx1, ty1, tz1, tx2, ty2, tz2) = self.transformWall(lineDef, debug)

        # PERSPECTIVE TRANSFORMED

        # Clip
        # determine clipping, if both z's < 0 its totally behind
        # if only 1 is negative it can be clipped
        if tz1 > 0 or tz2 > 0:
            # if line crosses the players view plane clip it
            # nearz = 1e-4, farz = 5, nearside = 1e-5f, farside = 20.f;
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

            # Do perspective transformation
            # xscale1 = lhfov / tz1
            # yscale1 = lvfov / tz1
            # x1 = (int)(surfaceWidth/2 - (int)(tx1 * xscale1))
            # xscale2 = lhfov / tz2
            # yscale2 = lvfov / tz2
            # x2 = (int)(surfaceWidth/2 - (int)(tx2 * xscale2))

            # if (x1 >= x2 || x2 < now.sx1 || x1 > now.sx2) continue; // Only render if it's visible

            # Acquire the floor and ceiling heights, relative to where the player's view is
            #yceil  = sect->ceil  - player.where.z;
            #yfloor = sect->floor - player.where.z;
            ceil = 10
            floor = -10
            yceil  = ceil - self.worldZ
            yfloor = floor - self.worldZ
            # print(surfaceHeight)

            # Project our ceiling & floor heights into screen coordinates (Y coordinate) */
            #define Yaw(y,z) (y + z*player.yaw)
            # y1a  = (int) ( surfaceHeight/2 - (int)(self.yaw(yceil, tz1) * yscale1) )
            # y1b = (int) ( surfaceHeight/2 - (int)(self.yaw(yfloor, tz1) * yscale1) )
            # y2a  = (int) ( surfaceHeight/2 - (int)(self.yaw(yceil, tz2) * yscale2) )
            # y2b = (int) ( surfaceHeight/2 - (int)(self.yaw(yfloor, tz2) * yscale2) )

            # return [x1, y1a], [x2, y2a], [x2, y2b], [x1, y1b],

            # Transform
            # 16 is effects FoV, the bigger the narrower
            # TODO: its either halfW or halfH, haven't figured it out, originally just "50"
            xscale1 = lhfov / tz1
            yscale1 = lvfov / tz1
            xscale2 = lhfov / tz2
            yscale2 = lvfov / tz2

            height = 10

            # huh = 32
            # x1 = -tx1 * huh / tz1
            # y1a = -halfH / tz1
            # y1b =  halfH / tz1
            # x2 = -tx2 * huh / tz2
            # y2a = -halfH / tz2
            # y2b =  halfH / tz2

            # return [halfW + x1, halfH + y1a], [halfW + x2, halfH + y2a], [halfW + x2, halfH + y2b], [halfW + x1, halfH + y1b],

            x1 = -(int)(tx1 * xscale1)
            # x1 = -tx1 * 16 / tz1
            # y1a = surfaceHeight/2 - (int)(self.yaw(yceil, tz1) * yscale1)
            y1a = -halfH / tz1 * height
            # y1b = -(int)(self.yaw(yfloor, tz1) * yscale1)
            y1b = halfH / tz1 * height

            x2 = -(int)(tx2 * xscale2)
            # x2 = -tx2 * 16 / tz2
            # y2a = -(int)(self.yaw(yceil, tz2) * yscale2)
            y2a = -halfH / tz2 * height
            # y2b = -(int)(self.yaw(yfloor, tz2) * yscale2)
            y2b = halfH / tz2 * height

            # if debug: print(-halfH, tz1, height, ' = ', y1a)

            # List of points
            return [halfW + x1, halfH + y1a], [halfW + x2, halfH + y2a], [halfW + x2, halfH + y2b], [halfW + x1, halfH + y1b],
            # get parts
            # topLine = [[halfW + x1, halfH + y1a], [halfW + x2, halfH + y2a]]
            # bottomLine = [[halfW + x1, halfH + y1b], [halfW + x2, halfH + y2b]]

            # leftLine = [[halfW + x1, halfH + y1a], [halfW + x1, halfH + y1b]]
            # rightLine = [[halfW + x2, halfH + y2a], [halfW + x2, halfH + y2b]]

            # return (topLine, rightLine, bottomLine, leftLine)

        return (None, None, None, None)
