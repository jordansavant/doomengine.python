import pygame, engine_ocl3, math, time, re
from engine_ocl.display import Display
from engine_ocl.eventlistener import EventListener

class Vector3(object):
    def __init__(self, x, y, z, w=1):
        self.x = x
        self.y = y
        self.z = z
        self.w = w # w component for sensible matrix math
    def clone(self):
        return Vector3(self.x, self.y, self.z)
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

class Triangle(object):
    def __init__(self):
        self.points = [None, None, None] # 3 Vector3's
        self.color = None # (r, g, b) tuple
    def clone(self):
        c = Triangle()
        for i, p in enumerate(self.points):
            c.points[i] = p.clone()
        return c

    @classmethod
    def fromPointList(cls, pl):
        t = cls()
        t.points = [Vector3(pl[0], pl[1], pl[2]), Vector3(pl[3], pl[4], pl[5]), Vector3(pl[6], pl[7], pl[8])]
        return t
    @classmethod
    def fromVectors(cls, v1, v2, v3):
        t = cls()
        t.points = [v1, v2, v3]
        return t

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

class Mesh(object):
    def __init__(self):
        self.triangles = []
    def loadFromObjFile(self, filename):
        # OBJ files are 3D model files
        # capable of loading from an obj file
        vertCache = []
        reType = re.compile('^([a-z0-9#]) ')
        reVert = re.compile('^v ([0-9.-]+) ([0-9.-]+) ([0-9.-]+)$')
        reFace = re.compile('^f ([0-9]+) ([0-9]+) ([0-9]+)$')
        with open(filename) as objFile:
            for line in objFile:
                typeMatches = reType.match(line)
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
                    self.triangles.append(Triangle.fromVectors(v1, v2, v3))

# START GAME

display = Display(640, 480)
listener = EventListener()
#pygame.mouse.set_visible(False)
#pygame.event.set_grab(True)

# OCL 1 was about creating the Perspective Matrix
# OCL 2 was complex 3d objects, depth sorting and hiding faces
# OCL 3 is camera work and clipping

# Perspective Projection matrix for camera
zNear = 0.1
zFar = 1000.0
fov = 90
projectionMatrix = Matrix4x4.MakeProjection(fov, display.aspectRatio, zNear, zFar)


# CUBE DEFINITION
# define triangle points in clockwise direction for a cube
# south
t1  = Triangle.fromPointList([0,0,0, 0,1,0, 1,1,0])
t2  = Triangle.fromPointList([0,0,0, 1,1,0, 1,0,0])
# east
t3  = Triangle.fromPointList([1,0,0, 1,1,0, 1,1,1])
t4  = Triangle.fromPointList([1,0,0, 1,1,1, 1,0,1])
# north
t5  = Triangle.fromPointList([1,0,1, 1,1,1, 0,1,1])
t6  = Triangle.fromPointList([1,0,1, 0,1,1, 0,0,1])
# west
t7  = Triangle.fromPointList([0,0,1, 0,1,1, 0,1,0])
t8  = Triangle.fromPointList([0,0,1, 0,1,0, 0,0,0])
# top
t9  = Triangle.fromPointList([0,1,0, 0,1,1, 1,1,1])
t10 = Triangle.fromPointList([0,1,0, 1,1,1, 1,1,0])
# bottom
t11 = Triangle.fromPointList([1,0,1, 0,0,1, 0,0,0])
t12 = Triangle.fromPointList([1,0,1, 0,0,0, 1,0,0])

meshCube = Mesh()
meshCube.triangles.append(t1)
meshCube.triangles.append(t2)
meshCube.triangles.append(t3)
meshCube.triangles.append(t4)
meshCube.triangles.append(t5)
meshCube.triangles.append(t6)
meshCube.triangles.append(t7)
meshCube.triangles.append(t8)
meshCube.triangles.append(t9)
meshCube.triangles.append(t10)
meshCube.triangles.append(t11)
meshCube.triangles.append(t12)


# OBJECT FILE DEFINITION
meshObj = Mesh();
meshObj.loadFromObjFile("resources/ocl_VideoShip.obj");


# Define a camera with a position in the world of 0,0,0
tempCamera = Vector3(0,0,0)

def drawTriangle(display, points, color, lineWidth):
    display.drawLine([[points[0].x, points[0].y], [points[1].x, points[1].y]], color, lineWidth)
    display.drawLine([[points[1].x, points[1].y], [points[2].x, points[2].y]], color, lineWidth)
    display.drawLine([[points[2].x, points[2].y], [points[0].x, points[0].y]], color, lineWidth)
def fillTriangle(display, points, color):
    display.drawPolygon([[points[0].x, points[0].y], [points[1].x, points[1].y], [points[2].x, points[2].y]], color, 0)

# give us a small title
font = pygame.font.Font(None, 28)
titletext = font.render("Math utilities and code refactored (press up for mode)", 1, (50, 50, 50));
textpos = titletext.get_rect(bottom = display.height - 10, centerx = display.width/2)


# Which shape are we rendering in this demo?
#renderMesh = meshCube
#renderOffsetZ = 3.0
renderMesh = meshObj
renderOffsetZ = 8.0
paintersAlgorithm = False

# visualizer mode for cube and obj
mode = 0
max_modes = 3
def mode_up():
    global renderMesh, renderOffsetZ, mode, max_modes
    mode = (mode + 1) % max_modes
listener.onKeyUp(pygame.K_UP, mode_up)

timeLapsed = 0
while True:

    if mode == 0:
        renderMesh = meshObj
        renderOffsetZ = 8.0
        paintersAlgorithm = True
    elif mode == 1:
        renderMesh = meshObj
        renderOffsetZ = 8.0
        paintersAlgorithm = False
    elif mode == 2:
        renderMesh = meshCube
        renderOffsetZ = 3.0
        paintersAlgorithm = False

    listener.update()
    display.start()

    display.drawText(titletext, textpos)

    # rotation values
    matRotZ = Matrix4x4.MakeRotationZ(timeLapsed / 2)
    matRotX = Matrix4x4.MakeRotationX(timeLapsed)

    # translation values
    matTrans = Matrix4x4.MakeTranslation(0, 0, renderOffsetZ)

    # create world matrix which is a combination of rotation and translation
    matWorld = Matrix4x4.MakeIdentity() # form world matrix
    matWorld = Matrix4x4.MultiplyMatrix4x4(matRotZ, matRotX) # Transform by Rotation by z and x
    matWorld = Matrix4x4.MultiplyMatrix4x4(matWorld, matTrans) # Transform by Translation

    # Draw triangles projected into our perspective
    painterTriangles = []
    for t in renderMesh.triangles:

        # Transform the triangle by world rotation and translation
        triTransformed = Triangle();
        triTransformed.points[0] = Matrix4x4.MultiplyVector(matWorld, t.points[0])
        triTransformed.points[1] = Matrix4x4.MultiplyVector(matWorld, t.points[1])
        triTransformed.points[2] = Matrix4x4.MultiplyVector(matWorld, t.points[2])

        # Calculate Normal and hide those facing away
        line1 = Vector3.Subtract(triTransformed.points[1], triTransformed.points[0])
        line2 = Vector3.Subtract(triTransformed.points[2], triTransformed.points[0])
        normal = Vector3.CrossProduct(line1, line2)
        normal = Vector3.Normalize(normal)
        # Get ray from camera to triangle
        cameraRay = Vector3.Subtract(triTransformed.points[0], tempCamera)

        # if ray is aligned with normal then its facing us and visible
        if (Vector3.DotProduct(normal, cameraRay) < 0):

            # Lets add some lighting for the triangle since its not culled
            lightDir = Vector3(0, 0, -1) # create a light coming out of the camera
            lightDir = Vector3.Normalize(lightDir)
            dot = Vector3.DotProduct(normal, lightDir)
            l = max(0, min(255, int(255.0 * dot)))

            # lets shade a color by this amount
            if mode == 0:
                color = (0, l, 0);
            elif mode == 1:
                color = (l, l, 0);
            else:
                color = (l, 0, l);
            triTransformed.color = color

            # Project our points to our perspective from World Space to Screen Space
            triProjected = Triangle()
            triProjected.color = triTransformed.color
            triProjected.points[0] = Matrix4x4.MultiplyVector(projectionMatrix, triTransformed.points[0])
            triProjected.points[1] = Matrix4x4.MultiplyVector(projectionMatrix, triTransformed.points[1])
            triProjected.points[2] = Matrix4x4.MultiplyVector(projectionMatrix, triTransformed.points[2])

            # Need to scale into view by dividing by the original Z depth that is now stored in the w component
            triProjected.points[0] = Vector3.Divide(triProjected.points[0], triProjected.points[0].w)
            triProjected.points[1] = Vector3.Divide(triProjected.points[1], triProjected.points[1].w)
            triProjected.points[2] = Vector3.Divide(triProjected.points[2], triProjected.points[2].w)

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

            # 6. Draw
            if paintersAlgorithm == False:
                # draw immediately
                fillTriangle(display, triProjected.points, triProjected.color);
                drawTriangle(display, triProjected.points, (0,0,0), 1)
            else:
                # draw after being depth sorted
                painterTriangles.append(triProjected);

    if paintersAlgorithm == True:
        # sort our painter triangles by their average z position
        def sortMethod(triangle):
            # get average z values from trianglea
            zAvg = (triangle.points[0].z + triangle.points[1].z + triangle.points[2].z) / 3
            return zAvg
        painterTriangles.sort(key=sortMethod, reverse=True)

        for triangle in painterTriangles:
            # draw in order of far to close
            fillTriangle(display, triangle.points, triangle.color);
            drawTriangle(display, triangle.points, (0,0,0), 1)

    display.end()
    time.sleep(1 / 60)
    timeLapsed += (1 / 60)
