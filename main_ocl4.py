import pygame, engine_ocl4, math, time, re, PIL
from engine_ocl4.display import Display
from engine_ocl4.eventlistener import EventListener
from PIL import Image

class Vector2(object): # for textures
    def __init__(self, u, v, w=1):
        self.u = u
        self.v = v
        self.w = w

class Vector3(object):
    def __init__(self, x, y, z, w=1):
        self.x = x
        self.y = y
        self.z = z
        self.w = w # w component for sensible matrix math
    def clone(self):
        return Vector3(self.x, self.y, self.z, self.w)
    def __str__(self):
        return "Vector3(" +str(self.x) + "," + str(self.y) + "," + str(self.z) + ")"
    def __repr__(self):
        return self.__str__()

    @staticmethod
    def Add(v1, v2):
        return Vector3(v1.x + v2.x, v1.y + v2.y, v1.z + v2.z)
    @staticmethod
    def Subtract(v1, v2):
        return Vector3(v1.x - v2.x, v1.y - v2.y, v1.z - v2.z)
    @staticmethod
    def Multiply(v1, k):
        return Vector3(v1.x * k, v1.y * k, v1.z * k)
    @staticmethod
    def Divide(v1, k):
        return Vector3(v1.x / k, v1.y / k, v1.z / k)
    @staticmethod
    def DotProduct(v1, v2):
        return v1.x * v2.x + v1.y * v2.y + v1.z * v2.z
    @staticmethod
    def Length(v):
        return math.sqrt(Vector3.DotProduct(v, v))
    @staticmethod
    def Normalize(v):
        l = Vector3.Length(v)
        return Vector3(v.x / l, v.y / l, v.z / l) if l != 0 else Vector3(0, 0, 0)
    @staticmethod
    def CrossProduct(v1, v2):
        x = v1.y * v2.z - v1.z * v2.y
        y = v1.z * v2.x - v1.x * v2.z
        z = v1.x * v2.y - v1.y * v2.x
        return Vector3(x, y, z)
    @staticmethod
    def CalcIntersection(vPlaneP, vPlaneN, vLineStart, vLineEnd):
        vPlaneN = Vector3.Normalize(vPlaneN)
        planeD = 0 - Vector3.DotProduct(vPlaneN, vPlaneP)
        a2d = Vector3.DotProduct(vLineStart, vPlaneN)
        b2d = Vector3.DotProduct(vLineEnd, vPlaneN)
        # t is a normalized value between 0 and 1 where the intersection occurs between the points
        t = (0 - planeD - a2d) / (b2d - a2d)
        return t
    @staticmethod
    def IntersectPlane(vPlaneP, vPlaneN, vLineStart, vLineEnd):
        t = Vector3.CalcIntersection(vPlaneP, vPlaneN, vLineStart, vLineEnd)
        lineStartToEnd = Vector3.Subtract(vLineEnd, vLineStart)
        lineToIntersect = Vector3.Multiply(lineStartToEnd, t)
        return Vector3.Add(vLineStart, lineToIntersect)


class Triangle(object):
    def __init__(self):
        self.points = [None, None, None] # 3 Vector3's
        self.texels = [None, None, None] # 3 Vector2's
        self.color = None # (r, g, b) tuple
    def clone(self):
        c = Triangle()
        for i, p in enumerate(self.points):
            c.points[i] = p.clone()
        c.color = self.color
        return c

    @classmethod
    def fromPointList(cls, pl, tl=None):
        t = cls()
        t.points = [Vector3(pl[0], pl[1], pl[2]), Vector3(pl[3], pl[4], pl[5]), Vector3(pl[6], pl[7], pl[8])]
        if tl != None:
            t.texels = [Vector2(tl[0], tl[1]), Vector2(tl[2], tl[3]), Vector2(tl[4], tl[5])]
        return t
    @classmethod
    def fromVectors(cls, v1, v2, v3):
        t = cls()
        t.points = [v1, v2, v3]
        return t
    @staticmethod
    def ClipAgainstPlane(vPlaneP, vPlaneN, triangle):
        # ensure plane normal is normal
        vPlaneN = Vector3.Normalize(vPlaneN)
        # define a distance from point to plane function, plane normal must be normalized
        def dist(p, vPlaneP, vPlaneN):
            n = Vector3.Normalize(p)
            return (vPlaneN.x * p.x + vPlaneN.y * p.y + vPlaneN.z * p.z - Vector3.DotProduct(vPlaneN, vPlaneP))

        # Get signed distance of each point in triangle to plane
        d0 = dist(triangle.points[0], vPlaneP, vPlaneN)
        d1 = dist(triangle.points[1], vPlaneP, vPlaneN)
        d2 = dist(triangle.points[2], vPlaneP, vPlaneN)

        insidePoints = [None, None, None]
        outsidePoints = [None, None, None]
        insidePointCount = 0
        outsidePointCount = 0
        insideTexels = [None, None, None]
        outsideTexels = [None, None, None]
        insideTexelCount = 0
        outsideTexelCount = 0

        # classify if points are inside or outside the plane and group them as such
        if d0 >= 0:
            insidePoints[insidePointCount] = triangle.points[0]
            insidePointCount += 1
            insideTexels[insideTexelCount] = triangle.texels[0]
            insideTexelCount += 1
        else:
            outsidePoints[outsidePointCount] = triangle.points[0]
            outsidePointCount += 1
            outsideTexels[outsideTexelCount] = triangle.texels[0]
            outsideTexelCount += 1
        if d1 >= 0:
            insidePoints[insidePointCount] = triangle.points[1]
            insidePointCount += 1
            insideTexels[insideTexelCount] = triangle.texels[1]
            insideTexelCount += 1
        else:
            outsidePoints[outsidePointCount] = triangle.points[1]
            outsidePointCount += 1
            outsideTexels[outsideTexelCount] = triangle.texels[1]
            outsideTexelCount += 1
        if d2 >= 0:
            insidePoints[insidePointCount] = triangle.points[2]
            insidePointCount += 1
            insideTexels[insideTexelCount] = triangle.texels[2]
            insideTexelCount += 1
        else:
            outsidePoints[outsidePointCount] = triangle.points[2]
            outsidePointCount += 1
            outsideTexels[outsideTexelCount] = triangle.texels[2]
            outsideTexelCount += 1

        # classify them into how to clip them
        if insidePointCount == 0:
            # all outside, clip entire triangle
            return []
        elif insidePointCount == 3:
            # all inside, return entire triangle alone
            return [triangle]
        elif insidePointCount == 1 and outsidePointCount == 2:
            # since two lie outside the plane, the triangle becomes a smaller triangle
            newTriangle = Triangle()
            newTriangle.color = triangle.color
            newTriangle.color = (triangle.color[0],0,0)
            # inside point is valid so keep it
            newTriangle.points[0] = insidePoints[0]
            newTriangle.texels[0] = insideTexels[0]

            # but two new points are at intersection of plane
            t = Vector3.CalcIntersection(vPlaneP, vPlaneN, insidePoints[0], outsidePoints[0])
            newTriangle.points[1] = Vector3.IntersectPlane(vPlaneP, vPlaneN, insidePoints[0], outsidePoints[0])
            newTriangle.texels[1] = Vector2(
                    t * (outsideTexels[0].u - insideTexels[0].u) + insideTexels[0].u,
                    t * (outsideTexels[0].v - insideTexels[0].v) + insideTexels[0].v,
                    t * (outsideTexels[0].w - insideTexels[0].w) + insideTexels[0].w)

            t = Vector3.CalcIntersection(vPlaneP, vPlaneN, insidePoints[0], outsidePoints[1])
            newTriangle.points[2] = Vector3.IntersectPlane(vPlaneP, vPlaneN, insidePoints[0], outsidePoints[1])
            newTriangle.texels[2] = Vector2(
                    t * (outsideTexels[1].u - insideTexels[0].u) + insideTexels[0].u,
                    t * (outsideTexels[1].v - insideTexels[0].v) + insideTexels[0].v,
                    t * (outsideTexels[1].w - insideTexels[0].w) + insideTexels[0].w)
            return [newTriangle]
        elif insidePointCount == 2 and outsidePointCount == 1:
            # since two lie inside and one outside it becomes a quad once clipped
            # so that quad needs to subdivide into 2 triangles
            newTriangle1 = Triangle()
            newTriangle1.color = triangle.color
            newTriangle1.color = (triangle.color[0], triangle.color[1], 0)

            newTriangle2 = Triangle()
            newTriangle2.color = triangle.color
            newTriangle2.color = (triangle.color[0], 0, triangle.color[2])

            # first triangle is two inside points connected to one intersection point
            newTriangle1.points[0] = insidePoints[0]
            newTriangle1.texels[0] = insideTexels[0]
            newTriangle1.points[1] = insidePoints[1]
            newTriangle1.texels[1] = insideTexels[1]
            t = Vector3.CalcIntersection(vPlaneP, vPlaneN, insidePoints[0], outsidePoints[0])
            newTriangle1.points[2] = Vector3.IntersectPlane(vPlaneP, vPlaneN, insidePoints[0], outsidePoints[0])
            newTriangle1.texels[2] = Vector2(
                    t * (outsideTexels[0].u - insideTexels[0].u) + insideTexels[0].u,
                    t * (outsideTexels[0].v - insideTexels[0].v) + insideTexels[0].v,
                    t * (outsideTexels[0].w - insideTexels[0].w) + insideTexels[0].w)

            # second triangle is one inside point, new intersection point and intersection point above
            newTriangle2.points[0] = insidePoints[1]
            newTriangle2.texels[0] = insideTexels[1]
            newTriangle2.points[1] = newTriangle1.points[2]
            newTriangle2.texels[1] = newTriangle1.texels[2]
            t = Vector3.CalcIntersection(vPlaneP, vPlaneN, insidePoints[0], outsidePoints[0])
            newTriangle2.points[2] = Vector3.IntersectPlane(vPlaneP, vPlaneN, insidePoints[1], outsidePoints[0])
            newTriangle2.texels[2] = Vector2(
                    t * (outsideTexels[0].u - insideTexels[1].u) + insideTexels[1].u,
                    t * (outsideTexels[0].v - insideTexels[1].v) + insideTexels[1].v,
                    t * (outsideTexels[0].w - insideTexels[1].w) + insideTexels[1].w)

            return [newTriangle1, newTriangle2]


class Matrix4x4(object):
    def __init__(self):
        # rows by cols
        self.m = [[0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0]]

    @staticmethod
    def MultiplyVector(m4, v3):
        x = v3.x * m4.m[0][0] + v3.y * m4.m[1][0] + v3.z * m4.m[2][0] + v3.w * m4.m[3][0]
        y = v3.x * m4.m[0][1] + v3.y * m4.m[1][1] + v3.z * m4.m[2][1] + v3.w * m4.m[3][1]
        z = v3.x * m4.m[0][2] + v3.y * m4.m[1][2] + v3.z * m4.m[2][2] + v3.w * m4.m[3][2]
        w = v3.x * m4.m[0][3] + v3.y * m4.m[1][3] + v3.z * m4.m[2][3] + v3.w * m4.m[3][3]
        return Vector3(x, y, z, w)
    @staticmethod
    def MakeIdentity():
        matrix = Matrix4x4()
        matrix.m[0][0] = 1.0;
        matrix.m[1][1] = 1.0;
        matrix.m[2][2] = 1.0;
        matrix.m[3][3] = 1.0;
        return matrix
    @staticmethod
    def MakeRotationX(angleRad):
        matrix = Matrix4x4()
        matrix.m[0][0] = 1.0
        matrix.m[1][1] = math.cos(angleRad)
        matrix.m[1][2] = math.sin(angleRad)
        matrix.m[2][1] = -math.sin(angleRad)
        matrix.m[2][2] = math.cos(angleRad)
        matrix.m[3][3] = 1.0
        return matrix
    @staticmethod
    def MakeRotationY(angleRad):
        matrix = Matrix4x4()
        matrix.m[0][0] = math.cos(angleRad)
        matrix.m[0][2] = math.sin(angleRad)
        matrix.m[2][0] = -math.sin(angleRad)
        matrix.m[1][1] = 1.0
        matrix.m[2][2] = math.cos(angleRad)
        matrix.m[3][3] = 1.0
        return matrix
    @staticmethod
    def MakeRotationZ(angleRad):
        matrix = Matrix4x4()
        matrix.m[0][0] = math.cos(angleRad)
        matrix.m[0][1] = math.sin(angleRad)
        matrix.m[1][0] = -math.sin(angleRad)
        matrix.m[1][1] = math.cos(angleRad)
        matrix.m[2][2] = 1.0
        matrix.m[3][3] = 1.0
        return matrix
    @staticmethod
    def MakeTranslation(x, y, z):
        matrix = Matrix4x4()
        matrix.m[0][0] = 1.0
        matrix.m[1][1] = 1.0
        matrix.m[2][2] = 1.0
        matrix.m[3][3] = 1.0
        matrix.m[3][0] = x
        matrix.m[3][1] = y
        matrix.m[3][2] = z
        return matrix
    @staticmethod
    def MakeProjection(fovDegrees, aspectRatio, zNear, zFar):
        fovRad = 1.0 / math.tan(fovDegrees * 0.5 / 180.0 * math.pi)
        matrix = Matrix4x4()
        matrix.m[0][0] = aspectRatio * fovRad
        matrix.m[1][1] = fovRad
        matrix.m[2][2] = zFar / (zFar - zNear)
        matrix.m[3][2] = (-zFar * zNear) / (zFar - zNear)
        matrix.m[2][3] = 1.0
        matrix.m[3][3] = 0.0
        return matrix
    @staticmethod
    def MultiplyMatrix4x4(m1, m2):
        matrix = Matrix4x4()
        for c in range(0, 4):
            for r in range(0, 4):
                matrix.m[r][c] = m1.m[r][0] * m2.m[0][c] + m1.m[r][1] * m2.m[1][c] + m1.m[r][2] * m2.m[2][c] + m1.m[r][3] * m2.m[3][c]
        return matrix;
    @staticmethod
    def PointAt(vPos, vTarget, vUp):
        # calculate new forward direction
        newForward = Vector3.Subtract(vTarget, vPos)
        newForward = Vector3.Normalize(newForward)

        # calculate new "Up" direction
        a = Vector3.Multiply(newForward, Vector3.DotProduct(vUp, newForward))
        newUp = Vector3.Subtract(vUp, a)
        newUp = Vector3.Normalize(newUp)

        # new right direction is easy, its just the cross product normal
        newRight = Vector3.CrossProduct(newUp, newForward)

        # create matrix to represent this translation
        matrix = Matrix4x4()
        matrix.m[0][0] = newRight.x
        matrix.m[0][1] = newRight.y
        matrix.m[0][2] = newRight.z
        matrix.m[0][3] = 0.0

        matrix.m[1][0] = newUp.x
        matrix.m[1][1] = newUp.y
        matrix.m[1][2] = newUp.z
        matrix.m[1][3] = 0.0

        matrix.m[2][0] = newForward.x
        matrix.m[2][1] = newForward.y
        matrix.m[2][2] = newForward.z
        matrix.m[2][3] = 0.0

        matrix.m[3][0] = vPos.x
        matrix.m[3][1] = vPos.y
        matrix.m[3][2] = vPos.z
        matrix.m[3][3] = 1.0
        return matrix
    @staticmethod
    def QuickInverse(m): # only works for rotation and translation matrices
        matrix = Matrix4x4()
        matrix.m[0][0] = m.m[0][0]
        matrix.m[0][1] = m.m[1][0]
        matrix.m[0][0] = m.m[0][0]
        matrix.m[0][2] = m.m[2][0]
        matrix.m[0][3] = 0.0

        matrix.m[1][0] = m.m[0][1]
        matrix.m[1][1] = m.m[1][1]
        matrix.m[1][2] = m.m[2][1]
        matrix.m[1][3] = 0.0

        matrix.m[2][0] = m.m[0][2]
        matrix.m[2][1] = m.m[1][2]
        matrix.m[2][2] = m.m[2][2]
        matrix.m[2][3] = 0.0

        matrix.m[3][0] = -(m.m[3][0] * matrix.m[0][0] + m.m[3][1] * matrix.m[1][0] + m.m[3][2] * matrix.m[2][0])
        matrix.m[3][1] = -(m.m[3][0] * matrix.m[0][1] + m.m[3][1] * matrix.m[1][1] + m.m[3][2] * matrix.m[2][1])
        matrix.m[3][2] = -(m.m[3][0] * matrix.m[0][2] + m.m[3][1] * matrix.m[1][2] + m.m[3][2] * matrix.m[2][2])
        matrix.m[3][3] = 1.0
        return matrix


class Mesh(object):
    def __init__(self):
        self.triangles = []
    @classmethod
    def loadCube(cls):
        # define triangle points in clockwise direction for a cube
        meshCube = cls()
        # south                                          points in space        texture
        meshCube.triangles.append(Triangle.fromPointList([0,0,0, 0,1,0, 1,1,0], [0,1, 0,0, 1,0]))
        meshCube.triangles.append(Triangle.fromPointList([0,0,0, 1,1,0, 1,0,0], [0,1, 1,0, 1,1]))
        # east
        meshCube.triangles.append(Triangle.fromPointList([1,0,0, 1,1,0, 1,1,1], [0,1, 0,0, 1,0]))
        meshCube.triangles.append(Triangle.fromPointList([1,0,0, 1,1,1, 1,0,1], [0,1, 1,0, 1,1]))
        # north
        meshCube.triangles.append(Triangle.fromPointList([1,0,1, 1,1,1, 0,1,1], [0,1, 0,0, 1,0]))
        meshCube.triangles.append(Triangle.fromPointList([1,0,1, 0,1,1, 0,0,1], [0,1, 1,0, 1,1]))
        # west
        meshCube.triangles.append(Triangle.fromPointList([0,0,1, 0,1,1, 0,1,0], [0,1, 0,0, 1,0]))
        meshCube.triangles.append(Triangle.fromPointList([0,0,1, 0,1,0, 0,0,0], [0,1, 1,0, 1,1]))
        # top
        meshCube.triangles.append(Triangle.fromPointList([0,1,0, 0,1,1, 1,1,1], [0,1, 0,0, 1,0]))
        meshCube.triangles.append(Triangle.fromPointList([0,1,0, 1,1,1, 1,1,0], [0,1, 1,0, 1,1]))
        # bottom
        meshCube.triangles.append(Triangle.fromPointList([1,0,1, 0,0,1, 0,0,0], [0,1, 0,0, 1,0]))
        meshCube.triangles.append(Triangle.fromPointList([1,0,1, 0,0,0, 1,0,0], [0,1, 1,0, 1,1]))
        return meshCube

    @classmethod
    def loadFromObjFile(cls, filename):
        # OBJ files are 3D model files
        # capable of loading from an obj file
        mesh = cls()
        vertCache = []
        reType = re.compile('^([a-z0-9#]) ')
        reVert = re.compile('^v ([0-9.-]+) ([0-9.-]+) ([0-9.-]+)$')
        reFace = re.compile('^f ([0-9]+) ([0-9]+) ([0-9]+)$')
        with open(filename) as objFile:
            for line in objFile:
                typeMatches = reType.match(line)
                if (typeMatches == None):
                    continue
                # Load Vertex data
                if (typeMatches[1] == 'v'):
                    vertMatches = reVert.match(line)
                    x = float(vertMatches[1])
                    y = float(vertMatches[2])
                    z = float(vertMatches[3])
                    vertCache.append(Vector3(x, y, z))
                # Load face data
                if (typeMatches[1] == 'f'):
                    # A face is a collection of indices of related vertices
                    faceMatches = reFace.match(line)
                    i1 = int(faceMatches[1])
                    i2 = int(faceMatches[2])
                    i3 = int(faceMatches[3])
                    # Annoyingly the index starts with 1, not 0
                    v1 = vertCache[i1 - 1]
                    v2 = vertCache[i2 - 1]
                    v3 = vertCache[i3 - 1]
                    mesh.triangles.append(Triangle.fromVectors(v1, v2, v3))
        return mesh


def drawTriangle(display, points, color, lineWidth):
    display.drawLine([[points[0].x, points[0].y], [points[1].x, points[1].y]], color, lineWidth)
    display.drawLine([[points[1].x, points[1].y], [points[2].x, points[2].y]], color, lineWidth)
    display.drawLine([[points[2].x, points[2].y], [points[0].x, points[0].y]], color, lineWidth)


def fillTriangle(display, points, color):
    display.drawPolygon([[points[0].x, points[0].y], [points[1].x, points[1].y], [points[2].x, points[2].y]], color, 0)

def rasterizeTriangle(display, x1, y1, u1, v1, w1,  x2, y2, u2, v2, w2,  x3, y3, u3, v3, w3, color, img, texture):
    x1 = int(x1); y1 = int(y1)
    x2 = int(x2); y2 = int(y2)
    x3 = int(x3); y3 = int(y3)
    if y2 < y1:
        y1, y2 = y2, y1
        x1, x2 = x2, x1
        u1, u2 = u2, u1
        v1, v2 = v2, v1
        w1, w2 = w2, w1

    if y3 < y1:
        y1, y3 = y3, y1
        x1, x3 = x3, x1
        u1, u3 = u3, u1
        v1, v3 = v3, v1
        w1, w3 = w3, w1

    if y3 < y2:
        y2, y3 = y3, y2
        x2, x3 = x3, x2
        u2, u3 = u3, u2
        v2, v3 = v3, v2
        w2, w3 = w3, w2

    dy1 = y2 - y1
    dx1 = x2 - x1
    dv1 = v2 - v1
    du1 = u2 - u1
    dw1 = w2 - w1

    dy2 = y3 - y1
    dx2 = x3 - x1
    dv2 = v3 - v1
    du2 = u3 - u1
    dw2 = w3 - w1

    tex_u=0; tex_v=0; tex_w=0;

    dax_step = 0; dbx_step = 0
    du1_step = 0; dv1_step = 0
    du2_step = 0; dv2_step = 0
    dw1_step=0; dw2_step=0

    if dy1:
        dax_step = dx1 / abs(dy1)
    if dy2:
        dbx_step = dx2 / abs(dy2)
    if dy1:
        du1_step = du1 / abs(dy1)
    if dy1:
        dv1_step = dv1 / abs(dy1)
    if dy1:
        dw1_step = dw1 / abs(dy1)
    if dy2:
        du2_step = du2 / abs(dy2)
    if dy2:
        dv2_step = dv2 / abs(dy2)
    if dy2:
        dw2_step = dw2 / abs(dy2)

    if dy1:

        for i in range(y1, y2+1):
            ax = int(x1 + (i - y1) * dax_step)
            bx = int(x1 + (i - y1) * dbx_step)

            tex_su = u1 + (i - y1) * du1_step
            tex_sv = v1 + (i - y1) * dv1_step
            tex_sw = w1 + (i - y1) * dw1_step

            tex_eu = u1 + (i - y1) * du2_step
            tex_ev = v1 + (i - y1) * dv2_step
            tex_ew = w1 + (i - y1) * dw2_step

            if ax > bx:
                ax, bx = bx, ax
                tex_su, tex_eu = tex_eu, tex_su
                tex_sv, tex_ev = tex_ev, tex_sv
                tex_sw, tex_ew = tex_ew, tex_sw

            tex_u = tex_su
            tex_v = tex_sv
            tex_w = tex_sw

            if bx - ax == 0:
                continue

            tstep = 1.0 / (bx - ax)
            t = 0.0

            for j in range(ax, bx):
                tex_u = (1.0 - t) * tex_su + t * tex_eu
                tex_v = (1.0 - t) * tex_sv + t * tex_ev
                tex_w = (1.0 - t) * tex_sw + t * tex_ew

                texX = int(tex_u * img.size[0]) - 1
                texY = int(tex_v * img.size[1]) - 1
                pixel = texture[texX, texY]
                lumens = color[0] / 255; # sample original lighting luminosity
                display.drawPixel([j,i], (pixel[0] * lumens, pixel[1] * lumens, pixel[2] * lumens)) #(233, 122, 1))
                #if (tex_w > pDepthBuffer[i*ScreenWidth() + j]):
                    #DrawPoint(j, i, tex->SampleGlyph(tex_u / tex_w, tex_v / tex_w), tex->SampleColour(tex_u / tex_w, tex_v / tex_w))
                    #pDepthBuffer[i*ScreenWidth() + j] = tex_w
                t += tstep

    dy1 = y3 - y2
    dx1 = x3 - x2
    dv1 = v3 - v2
    du1 = u3 - u2
    dw1 = w3 - w2

    if (dy1):
        dax_step = dx1 / abs(dy1)
    if (dy2):
        dbx_step = dx2 / abs(dy2)

    du1_step = 0; dv1_step = 0
    if dy1:
        du1_step = du1 / abs(dy1)
    if dy1:
        dv1_step = dv1 / abs(dy1)
    if dy1:
        dw1_step = dw1 / abs(dy1)

    if dy1:
        for i in range(y2, y3+1):
            ax = int(x2 + (i - y2) * dax_step)
            bx = int(x1 + (i - y1) * dbx_step)

            tex_su = u2 + (i - y2) * du1_step
            tex_sv = v2 + (i - y2) * dv1_step
            tex_sw = w2 + (i - y2) * dw1_step

            tex_eu = u1 + (i - y1) * du2_step
            tex_ev = v1 + (i - y1) * dv2_step
            tex_ew = w1 + (i - y1) * dw2_step

            if ax > bx:
                ax, bx = bx, ax
                tex_su, tex_eu = tex_eu, tex_su
                tex_sv, tex_ev = tex_ev, tex_sv
                tex_sw, tex_ew = tex_ew, tex_sw

            tex_u = tex_su
            tex_v = tex_sv
            tex_w = tex_sw

            if bx - ax == 0:
                continue

            tstep = 1.0 / float(bx - ax)
            t = 0.0

            for j in range(ax, bx):
                tex_u = (1.0 - t) * tex_su + t * tex_eu
                tex_v = (1.0 - t) * tex_sv + t * tex_ev
                tex_w = (1.0 - t) * tex_sw + t * tex_ew

                texX = int(tex_u * img.size[0]) - 1
                texY = int(tex_v * img.size[1]) - 1
                pixel = texture[texX, texY]
                lumens = color[0] / 255; # sample original lighting luminosity
                display.drawPixel([j,i], (pixel[0] * lumens, pixel[1] * lumens, pixel[2] * lumens)) #(233, 122, 1))
                #if (tex_w > pfDepthBuffer[i*ScreenWidth() + j]):
                    #DrawPoint(j, i, tex->SampleGlyph(tex_u / tex_w, tex_v / tex_w), tex->SampleColour(tex_u / tex_w, tex_v / tex_w))
                    #pDepthBuffer[i*ScreenWidth() + j] = tex_w
                t += tstep


# OCL 1 was about creating the Perspective Matrix
# OCL 2 was complex 3d objects, depth sorting and hiding faces
# OCL 3 is camera work and clipping
# OCL 4 is about texture loading and depth buffering -- Python really starts to fall apart here as a full 3D engine in CPU

# START GAME
# load test texture
img = Image.open('resources/doomtex.png') # Can be many different formats.
pix = img.load()

# load display
display = Display(1024, 768)
listener = EventListener()
#pygame.mouse.set_visible(False)
#pygame.event.set_grab(True)

# PERSPECTIVE PROJECTION MATRIX FOR CAMERA
zNear = 0.1
zFar = 1000.0
fov = 90
projectionMatrix = Matrix4x4.MakeProjection(fov, display.aspectRatio, zNear, zFar)

# MESHES
meshes = []
meshes.append(Mesh.loadCube())
#meshes.append(Mesh.loadFromObjFile("resources/ocl_axis.obj"))
#meshes.append(Mesh.loadFromObjFile("resources/ocl_spaceship.obj"))
#meshes.append(Mesh.loadFromObjFile("resources/ocl_teapot.obj"))
# meshes.append(Mesh.loadFromObjFile("resources/ocl_mountains.obj")) # performance is TERRIBLE with my non-optimized python engine, this will be a good test file for improvements

# give us a small title
font = pygame.font.Font(None, 28)
titletext = font.render("Camera Movement and Clipping with Subtriangles (press UP for mode)", 1, (50, 50, 50))
textpos = titletext.get_rect(bottom = display.height - 10, centerx = display.width/2)

# CAMERA PROPERTIES
vCamera = Vector3(0, 0, 0) # location of camera in world space
vLookDir = Vector3(0, 0, 0) # direction camera is looking
yaw = 0 # FPS camera rotation in XZ
renderOffsetZ = 8.0
moveSpeed = 6.0
turnSpeed = 4.0

# INPUT LISTENErS
mode = 0
max_modes = len(meshes)
def mode_up():
    global mode, max_modes
    mode = (mode + 1) % max_modes
listener.onKeyUp(pygame.K_UP, mode_up)

inputAscend = False
inputDescend = False
inputForward = False
inputBackward = False
inputStrafeLeft = False
inputStrafeRight = False
inputTurnLeft = False
inputTurnRight = False
def on_z_down():
    global inputAscend; inputAscend = True
listener.onKeyDown(pygame.K_z, on_z_down)
def on_z_up():
    global inputAscend; inputAscend = False
listener.onKeyUp(pygame.K_z, on_z_up)
def on_x_down():
    global inputDescend; inputDescend = True
listener.onKeyDown(pygame.K_x, on_x_down)
def on_x_up():
    global inputDescend; inputDescend = False
listener.onKeyUp(pygame.K_x, on_x_up)

def on_w_down():
    global inputForward; inputForward = True
listener.onKeyDown(pygame.K_w, on_w_down)
def on_w_up():
    global inputForward; inputForward = False
listener.onKeyUp(pygame.K_w, on_w_up)
def on_s_down():
    global inputBackward; inputBackward = True
listener.onKeyDown(pygame.K_s, on_s_down)
def on_s_up():
    global inputBackward; inputBackward = False
listener.onKeyUp(pygame.K_s, on_s_up)
def on_a_down():
    global inputStrafeLeft; inputStrafeLeft = True
listener.onKeyDown(pygame.K_a, on_a_down)
def on_a_up():
    global inputStrafeLeft; inputStrafeLeft = False
listener.onKeyUp(pygame.K_a, on_a_up)
def on_d_down():
    global inputStrafeRight; inputStrafeRight = True
listener.onKeyDown(pygame.K_d, on_d_down)
def on_d_up():
    global inputStrafeRight; inputStrafeRight = False
listener.onKeyUp(pygame.K_d, on_d_up)

def on_left_down():
    global inputTurnLeft; inputTurnLeft = True
listener.onKeyDown(pygame.K_LEFT, on_left_down)
def on_left_up():
    global inputTurnLeft; inputTurnLeft = False
listener.onKeyUp(pygame.K_LEFT, on_left_up)
def on_right_down():
    global inputTurnRight; inputTurnRight = True
listener.onKeyDown(pygame.K_RIGHT, on_right_down)
def on_right_up():
    global inputTurnRight; inputTurnRight = False
listener.onKeyUp(pygame.K_RIGHT, on_right_up)

def rotate2d(x, y, rads):
    cos = math.cos(rads)
    sin = math.sin(rads)
    return [(x * cos) - (y * sin), (x * sin) + (y * cos)]

# GAME LOOP
timeLapsed = 0
deltaTime = 1/60
while True:

    # INPUT UPDATE
    listener.update()

    if inputAscend:
        vCamera.y += moveSpeed * deltaTime
    if inputDescend:
        vCamera.y -= moveSpeed * deltaTime

    vForward = Vector3.Multiply(vLookDir, moveSpeed * deltaTime)
    # calculate left strafe
    # option 1, forcing horizontal strafing only, rotate a vector comprised of forward x and forward z by Pi/2
    # option 2, calculate normal of Z vector and Y vector
    #vLeftP = rotate2d(vForward.x, vForward.z, math.pi/2)
    if (inputForward):
        vCamera = Vector3.Add(vCamera, vForward)
    if (inputBackward):
        vCamera = Vector3.Subtract(vCamera, vForward)
    if (inputStrafeLeft):
        vLeft = Vector3.CrossProduct(vForward, Vector3(0, 1, 0))
        vCamera = Vector3.Subtract(vCamera, vLeft)
    if (inputStrafeRight):
        vLeft = Vector3.CrossProduct(vForward, Vector3(0, 1, 0))
        vCamera = Vector3.Add(vCamera, vLeft)

    if (inputTurnLeft):
        yaw -= turnSpeed * deltaTime
    if (inputTurnRight):
        yaw += turnSpeed * deltaTime


    # UPDATE
    renderMesh = meshes[mode]

    # rotation values
    theta = 0
    # theta += deltaTime
    matRotZ = Matrix4x4.MakeRotationZ(theta / 2)
    matRotX = Matrix4x4.MakeRotationX(theta)

    # translation values
    matTrans = Matrix4x4.MakeTranslation(0, 0, renderOffsetZ)

    # create world matrix which is a combination of rotation and translation
    matWorld = Matrix4x4.MakeIdentity() # form world matrix
    matWorld = Matrix4x4.MultiplyMatrix4x4(matRotZ, matRotX) # Transform by Rotation by z and x
    matWorld = Matrix4x4.MultiplyMatrix4x4(matWorld, matTrans) # Transform by Translation

    # create "point at" matrix for camer
    vUp = Vector3(0, -1, 0) # set y to negative 1 because screen coords of y are positive going down
    vTarget = Vector3(0, 0, 1)
    matCameraRotation = Matrix4x4.MakeRotationY(yaw)
    vLookDir = Matrix4x4.MultiplyVector(matCameraRotation, vTarget)
    vTarget = Vector3.Add(vCamera, vLookDir)
    matCamera = Matrix4x4.PointAt(vCamera, vTarget, vUp)

    # Make a view matrix from camera (which is the reverse of the camera)
    matView = Matrix4x4.QuickInverse(matCamera)

    # Draw triangles projected into our perspective
    painterTriangles = []
    for t in renderMesh.triangles:

        # Transform the triangle by world rotation and translation
        triTransformed = Triangle();
        triTransformed.points[0] = Matrix4x4.MultiplyVector(matWorld, t.points[0])
        triTransformed.points[1] = Matrix4x4.MultiplyVector(matWorld, t.points[1])
        triTransformed.points[2] = Matrix4x4.MultiplyVector(matWorld, t.points[2])
        triTransformed.texels[0] = t.texels[0]
        triTransformed.texels[1] = t.texels[1]
        triTransformed.texels[2] = t.texels[2]

        # Calculate Normal and hide those facing away
        line1 = Vector3.Subtract(triTransformed.points[1], triTransformed.points[0])
        line2 = Vector3.Subtract(triTransformed.points[2], triTransformed.points[0])
        normal = Vector3.CrossProduct(line1, line2)
        normal = Vector3.Normalize(normal)
        # Get ray from camera to triangle
        cameraRay = Vector3.Subtract(triTransformed.points[0], vCamera)

        # if ray is aligned with normal then its facing us and visible
        if (Vector3.DotProduct(normal, cameraRay) < 0):

            # Lets add some lighting for the triangle since its not culled
            lightDir = Vector3(.5, .5, -1) # create a light coming out of the camera
            lightDir = Vector3.Normalize(lightDir)
            dot = Vector3.DotProduct(normal, lightDir)
            l = max(50, min(255, int(255.0 * dot))) # global lighting some

            # lets shade a color by this amount
            color = (l, l, l);
            triTransformed.color = color

            # Convert world space to view Space
            triViewed = Triangle()
            triViewed.points[0] = Matrix4x4.MultiplyVector(matView, triTransformed.points[0])
            triViewed.points[1] = Matrix4x4.MultiplyVector(matView, triTransformed.points[1])
            triViewed.points[2] = Matrix4x4.MultiplyVector(matView, triTransformed.points[2])
            triViewed.texels[0] = triTransformed.texels[0]
            triViewed.texels[1] = triTransformed.texels[1]
            triViewed.texels[2] = triTransformed.texels[2]
            triViewed.color = triTransformed.color

            # Clip our triangles against our near and far Z frustrums
            clippedTriangles = Triangle.ClipAgainstPlane(Vector3(0,0,.25), Vector3(0,0,1), triViewed)

            for clippedTriangle in clippedTriangles:

                # Project our points to our perspective from World Space to Screen Space
                triProjected = Triangle()
                triProjected.color = clippedTriangle.color

                # copy texture
                triProjected.texels[0] = clippedTriangle.texels[0]
                triProjected.texels[1] = clippedTriangle.texels[1]
                triProjected.texels[2] = clippedTriangle.texels[2]

                # copy points
                triProjected.points[0] = Matrix4x4.MultiplyVector(projectionMatrix, clippedTriangle.points[0])
                triProjected.points[1] = Matrix4x4.MultiplyVector(projectionMatrix, clippedTriangle.points[1])
                triProjected.points[2] = Matrix4x4.MultiplyVector(projectionMatrix, clippedTriangle.points[2])

                # Need to scale into view by dividing by the original Z depth that is now stored in the w component
                triProjected.points[0] = Vector3.Divide(triProjected.points[0], triProjected.points[0].w)
                triProjected.points[1] = Vector3.Divide(triProjected.points[1], triProjected.points[1].w)
                triProjected.points[2] = Vector3.Divide(triProjected.points[2], triProjected.points[2].w)

                # scale texture
                triProjected.texels[0].u = triProjected.texels[0].u / triProjected.points[0].w;
                triProjected.texels[1].u = triProjected.texels[1].u / triProjected.points[1].w;
                triProjected.texels[2].u = triProjected.texels[2].u / triProjected.points[2].w;

                triProjected.texels[0].v = triProjected.texels[0].v / triProjected.points[0].w;
                triProjected.texels[1].v = triProjected.texels[1].v / triProjected.points[1].w;
                triProjected.texels[2].v = triProjected.texels[2].v / triProjected.points[2].w;

                triProjected.texels[0].w = 1.0 / triProjected.points[0].w;
                triProjected.texels[1].w = 1.0 / triProjected.points[1].w;
                triProjected.texels[2].w = 1.0 / triProjected.points[2].w;

                # Scale into viewport
                # points between -1 and -1 are within our screens FoV
                # so we want something at 0,0 to be at the center of the view, -1,0 at left, 0,1 at bottom etc
                # start by shifting the normalized x,y points to the range 0-2
                offsetView = Vector3(1, 1, 0)
                triProjected.points[0] = Vector3.Add(triProjected.points[0], offsetView)
                triProjected.points[1] = Vector3.Add(triProjected.points[1], offsetView)
                triProjected.points[2] = Vector3.Add(triProjected.points[2], offsetView)
                # divide the points by 2 and then multiply by size of screen
                # so something at -1 becomes 0/2=0 (left side) and +1 becomes 2/2=1 (right side)
                # something at 1 then becomes the size of the screen
                triProjected.points[0].x *= .5 * display.width
                triProjected.points[0].y *= .5 * display.height
                triProjected.points[1].x *= .5 * display.width
                triProjected.points[1].y *= .5 * display.height
                triProjected.points[2].x *= .5 * display.width
                triProjected.points[2].y *= .5 * display.height

                painterTriangles.append(triProjected);

    # sort our painter triangles by their average z position
    def sortMethod(triangle):
        # get average z values from trianglea
        zAvg = (triangle.points[0].z + triangle.points[1].z + triangle.points[2].z) / 3
        return zAvg
    painterTriangles.sort(key=sortMethod, reverse=True)


    # DRAW
    display.start()

    display.drawText(titletext, textpos)

    for triangle in painterTriangles:
        # clip triangles against screen edges (z clipping already done above)
        # since this can generate more triangles to render we will use a queue
        tQueue = []
        tQueue.append(triangle)
        newTriangleCount = 1

        for p in range(0, 4):
            trisToAdd = 0
            while newTriangleCount > 0:
                test = tQueue.pop(0)
                newTriangleCount -= 1
                # clip against screen planes, we only need to test each subsequent
                # plane against subsequent new triangles because all triangles after
                # a clip are inside the plane
                newTriangles = []
                if p == 0:
                    newTriangles = Triangle.ClipAgainstPlane(Vector3(0,0,0), Vector3(0,1,0), test)
                elif p == 1:
                    newTriangles = Triangle.ClipAgainstPlane(Vector3(0,display.height - 1,0), Vector3(0,-1,0), test)
                elif p == 2:
                    newTriangles = Triangle.ClipAgainstPlane(Vector3(0,0,0), Vector3(1,0,0), test)
                elif p == 3:
                    newTriangles = Triangle.ClipAgainstPlane(Vector3(display.width - 1,0,0), Vector3(-1,0,0), test)

                # append newly created triangles to queue so they can be
                # clipped against planes
                for t in newTriangles:
                    tQueue.append(t)
            newTriangleCount = len(tQueue)

        for final in tQueue:
            # draw in order of far to close
            #fillTriangle(display, final.points, final.color);
            #drawTriangle(display, final.points, (0,0,0), 1)
            rasterizeTriangle(display, final.points[0].x, final.points[0].y, final.texels[0].u, final.texels[0].v, final.texels[0].w,
				       final.points[1].x, final.points[1].y, final.texels[1].u, final.texels[1].v, final.texels[1].w,
				       final.points[2].x, final.points[2].y, final.texels[2].u, final.texels[2].v, final.texels[2].w,
                                       final.color, img, pix)
            #drawTriangle(display, final.points, (255,255,255), 1)

    display.end()
    time.sleep(1 / 60)
    timeLapsed += (1 / 60)
