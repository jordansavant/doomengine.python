import sys, pygame, math, time, numpy as np


# CONVENTIONS
# Vector3s are represented with a three element slice
# [ x, y, z ] for positions and rotations in 3d
#
# When reading matrix documentations they multiply
# left to right
# X = M . N . T
# means T times N times M in that order
#
# When reading matrix documentations consider their
# format for Column Major vs Row Major data layout
# I <believe?> I have used Column Major matrices
# [
#   [c1r1, c2r1, c3r1, c4r1]
#   [c1r2, c2r2, c3r2, c4r2]
#   [c1r3, c2r3, c3r3, c4r3]
#   [c1r4, c2r4, c3r4, c4r4]
# ]

# Two matrices multiplied together and summed to produce a scalar
# same as dot product ?
def matmul(matrix, matrixB):
    colsA = len(matrix[0])
    colsB = len(matrixB[0])
    rowsA = len(matrix)
    rowsB = len(matrixB)

    if colsA != rowsB:
        print("matmul mismatch")
        print(matrix, matrixB)
        print(colsA, colsB, rowsA, rowsB)
        sys.exit(1)

    r = []
    for j in range(rowsA):
        r.append([])
        for i in range(colsB):
            summ = 0
            for n in range(colsA):
                summ += matrix[j][n] * matrixB[n][i]
            r[j].append(summ)
    return r

def matinverse(matrix):
    return np.linalg.inv(matrix)

# NUMPY TEST
#A = [
#    [1, 3, 3],
#    [1, 4, 3],
#    [1, 3, 4]
#]
#B = np.linalg.inv(A)
#print(B)
#I = matmul(A, B)
#print(I)
#sys.exit()

class Cube(object):
    def __init__(self):
        self.worldPos = [0, 0, 0] # x, y, z coords
        self.worldRot = [0.0, 0.0, 0.0] # x, y, z rotations in radians
        self.worldScale = [100, 100, 100] # x, y, z axis scaling in world
        self.points = []

        a3 = [-1, -1, -1]
        b3 = [ 1, -1, -1]
        c3 = [ 1,  1, -1]
        d3 = [-1,  1, -1]

        e3 = [-1, -1, 1]
        f3 = [ 1, -1, 1]
        g3 = [ 1,  1, 1]
        h3 = [-1,  1, 1]
        self.points = [a3, b3, c3, d3,   e3, f3, g3, h3] # two sides of cube

    def getModelToWorldTransform(self):
        # FULL STEPS
        # 1. M > TRANSFORM MODEL TO WORLD SPACE
        # 2. V > TRANSFORM WORLD TO VIEW SPACE (CAMERA SPACE)
        # 3. P > TRANSFORM VIEW TO PROJECTION

        # M
        # DETERMINE WORLD TRANSFORMATION MATRIX
        # http://www.codinglabs.net/article_world_view_projection_matrix.aspx
        # we can translate, rotate and scale a
        # with a single transformation matrix.
        # Ordering is important:
        # 1. scale
        # 2. rotate
        # 3. translate

        # SCALE OUR CUBE
        # I defined the model in unit space and
        # need to scale the model to world space
        scale = [
            [self.worldScale[0], 0, 0, 0],
            [0, self.worldScale[1], 0, 0],
            [0, 0, self.worldScale[2], 0],
            [0, 0, 0, 1]
        ]
        transform = scale

        # ROTATE THE CUBE IN 3D SPACE
        # we can calculate the rotation in each axis
        # based on whatever the angle for that axis is
        rotationX = [
            [1, 0, 0, 0],
            [0, math.cos(self.worldRot[0]), - math.sin(self.worldRot[0]), 0],
            [0, math.sin(self.worldRot[0]),   math.cos(self.worldRot[0]), 0],
            [0, 0, 0, 1]
        ]
        rotationY = [
            [math.cos(self.worldRot[1]), 0, - math.sin(self.worldRot[1]), 0],
            [0, 1, 0, 0],
            [math.sin(self.worldRot[1]), 0,   math.cos(self.worldRot[1]), 0],
            [0, 0, 0, 1]
        ]
        rotationZ = [
            [math.cos(self.worldRot[2]), - math.sin(self.worldRot[2]), 0, 0],
            [math.sin(self.worldRot[2]),   math.cos(self.worldRot[2]), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ]
        transform = matmul(rotationX, transform)
        transform = matmul(rotationY, transform)
        transform = matmul(rotationZ, transform)

        # TRANSLATE FROM MODEL SPACE (-1, 1) TO WORLD SPACE
        # keeping the points in model space around the
        # model's origin, we can give the whole self a
        # world position and translate our model to that
        # position by placing its world position in the
        # final column for x, y, z
        translation = [
            [1, 0, 0, self.worldPos[0]],
            [0, 1, 0, self.worldPos[1]],
            [0, 0, 1, self.worldPos[2]],
            [0, 0, 0, 1]
        ]
        ModelToWorldTransform = matmul(translation, transform)

        return ModelToWorldTransform

class Camera(object):
    def __init__(self):
        self.worldPos = [0, 0, 0]
        self.worldRot = [0.0, 0.0, 0.0]

    def getCameraToWorldTransform(self):
        # FULL STEPS
        # less than cube model because we don't
        # scale a camera

        # M
        # DETERMINE WORLD TRANSFORMATION MATRIX

        # ROTATE THE CAMERA IN 3D SPACE
        # we can calculate the rotation in each axis
        # based on whatever the angle for that axis is
        rotationX = [
            [1, 0, 0, 0],
            [0, math.cos(self.worldRot[0]), - math.sin(self.worldRot[0]), 0],
            [0, math.sin(self.worldRot[0]),   math.cos(self.worldRot[0]), 0],
            [0, 0, 0, 1]
        ]
        rotationY = [
            [math.cos(self.worldRot[1]), 0, - math.sin(self.worldRot[1]), 0],
            [0, 1, 0, 0],
            [math.sin(self.worldRot[1]), 0,   math.cos(self.worldRot[1]), 0],
            [0, 0, 0, 1]
        ]
        rotationZ = [
            [math.cos(self.worldRot[2]), - math.sin(self.worldRot[2]), 0, 0],
            [math.sin(self.worldRot[2]),   math.cos(self.worldRot[2]), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ]
        transform = rotationX
        transform = matmul(rotationY, transform)
        transform = matmul(rotationZ, transform)

        # TRANSLATE FROM MODEL SPACE (-1, 1) TO WORLD SPACE
        # keeping the points in model space around the
        # model's origin, we can give the whole self a
        # world position and translate our model to that
        # position by placing its world position in the
        # final column for x, y, z
        translation = [
            [1, 0, 0, self.worldPos[0]],
            [0, 1, 0, self.worldPos[1]],
            [0, 0, 1, self.worldPos[2]],
            [0, 0, 0, 1]
        ]
        CameraToWorldTransform = matmul(translation, transform)

        return CameraToWorldTransform


screenW = 720
screenH = 720
pygame.init()
screen = pygame.display.set_mode((screenW, screenH), 0, 32)

# CREATE OBJECTS FOR RENDERING
cube = Cube()
camera = Camera()

def inputlisten():
    # "INPUT LISTENING" LOOP
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                sys.exit(0)

def update():
    # "UPDATE" LOOP
    # rotate cube
    cube.worldRot[0] = math.pi / 3
    cube.worldRot[1] += 0.01
    cube.worldPos[2] = 0

    camera.worldRot[2] += .01

def draw():
    # "DRAW" LOOP
    screen.fill((200, 200, 200))


    # M
    # GET CUBE MODEL TO WORLD TRANSFORMATION MATRIX
    ModelToWorldTransform = cube.getModelToWorldTransform()

    # V
    # FIND THE CAMERA POSITION IN WORLD SPACE
    CameraToWorldTransform = camera.getCameraToWorldTransform()

    # GET THE INVERSE (VIEW SPACE) AND APPLY IT TO THE MODEL
    CameraInverse = matinverse(CameraToWorldTransform)
    ViewSpace = matmul(CameraInverse, ModelToWorldTransform)

    # REPOSITION AND PROJECT EACH POINT
    projectedPoints = []
    for i in range(len(cube.points)):


        # MULTIPLY TRANSFORMATION MATRIX TO POSITION
        # convert vector3 into a 1col matrix
        point = cube.points[i]
        p = [[point[0]], [point[1]], [point[2]], [1]]
        transformed = matmul(ViewSpace, p)


        # P ATTEMPT AGAIN OFF NEW VIEW SPACE
        # ORTHOGRAPHIC
        width = 2
        height = 2
        znear = 1
        zfar = 100
        ortho1 = [
            [1/width, 0, 0, 0],
            [0, 1/height, 0, 0],
            [0, 0, -2/(zfar - znear), - (zfar + znear) / (zfar - znear)],
            [0, 0, 0, 1]
        ]

        # PERSPECTIVE
        # attempting while ignoring that it cops
        # out its tut and says the "GPU" will do
        # it for you
        fovx = 1
        fovy = .75
        persp1 = [
            [math.atan(fovx/2), 0, 0, 0],
            [0, math.atan(fovy/2), 0, 0],
            [0, 0, -((zfar + znear)/(zfar - znear)), -((2 * (znear * zfar)) / (zfar - znear))],
            [0, 0, -1, 0],
        ]



        # P
        # http://ogldev.atspace.co.uk/www/tutorial12/tutorial12.html
        # Perspective projection transformation requires 4 params
        # 1. The aspect ratio: the ratio between the width and the height of the rectangular area which will be the target of projection
        # 2. The vertical field of view: the vertical angle of the camera through which we are looking at the world
        # ?? Horizontal Field of View ??
        # 3. The location of the near Z plane: allows us to clip objects that are too close to the camera
        # 4. The location of the near Z plane: allows us to clip objects that are too close to the camera

        # Aspect Ratio = screen width / screen height
        aspectRatio = screenW / screenH
        #  . _ +1 _ .
        #  |        |
        # -ar      +ar   wider width than height has ar > 1
        #  |        |
        #  . _ -1 _ .
        #
        # projection plane is a rectangle that sits
        # in front of the camera
        #
        # distance from camera to projection plane using the vertical field of view:
        # vertFov is up to us to deterime, radians?
        # tan(vertFoV / 2) = 1 / dist
        # dist = 1 / tan(vertFoV / 2)
        #
        # now we find the projection of a points 3d coords on 2d projection
        # yProj / dist = y / z
        # yProj = (y * dist) / z = y / (z * tan(vertFov / 2))
        #
        # xProj / dist = x / z
        # xProj = (x * dist) / z = x ( z * tan(vertFov / 2))
        #
        # we know the point is in our projection plane if
        # it is within our projection window defined:
        # -ar < x < +ar
        # -1 < y < +1
        #
        # yProj is normalized between -1 and +1
        # xProj is not, its between aspect ratio +-
        # we can normalize xProj
        # xProj = x / ( aspectRatio * z * tan(vertFov / 2) )
        # yProj = y / ( z * tan(vertFov / 2) )
        #
        # whole lotta b.s. about how OpenGL does z division for us?
        #
        nearZ = -100 # picked at random
        farZ = 100 # picked at random
        vertFov = .95 # picked at random
        per1 = [
            [1 / (math.tan(vertFov / 2)), 0, 0, 0],
            [0, 1 / math.tan(vertFov / 2), 0, 0],
            [0, 0, 0, 0],
            [0, 0, 1, 0]
        ]
        per2 = [
            [1 / (aspectRatio * math.tan(vertFov / 2)), 0, 0, 0],
            [0, 1 / math.tan(vertFov / 2), 0, 0],
            [0, 0, (-nearZ - farZ) / (nearZ - farZ), (2 * farZ * nearZ / nearZ - farZ)],
            [0, 0, 1, 0]
        ]
        # above seems incomplete attempts since the tut
        # ended with opengl doing part of the work for us


        # https://www.scratchapixel.com/lessons/3d-basic-rendering/perspective-and-orthographic-projection-matrix/building-basic-perspective-projection-matrix
        # divide x and y by negative z since the camera
        # faces in the negative z direction
        # xProj = x / -z
        # yProj = y / -z
        # zProj = -z / -z = 1
        # also it maps wProj = -z ?
        # - far / (far - near)
        # - (far * near) / (far - near)
        #near = 0.1 # made up
        #far = 100 # made up
        #z = transformed[2][0];
        #per1 = [
        #    [1/-z, 0, 0, 0],
        #    [0, 1/-z, 0, 0],
        #    [0, 0, 1, 0],
        #    [0, 0, 0, 1]
        #]
        #fov = .75
        #s = 1 / math.tan(fov / 2)
        #per2 = [
        #    [s, 0, 0, 0],
        #    [0, s, 0, 0],
        #    [0, 0, - (far/(far - near)), -1],
        #    [0, 0, - (far * near / far - near), 0]
        #]
        #per3 = matmul(per1, per2)

        # CALCULATE PROJECTION MATRIX
        orthographicProjection = [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ]
        # reduce x and y when z is further away
        # center of cube is at -z is in front of us (at -1)
        # pushing it away by three lets us see it
        #distance = 0.0
        z = transformed[2][0];
        #z = 1 / (distance - rotated[2][0])
        perspectiveProjection = [
            [1/-z, 0, 0, 0],
            [0, 1/-z, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ]

        #projection = perspectiveProjection
        #projection = orthographicProjection
        #projection = per2
        #projection = ortho1
        projection = persp1

        # project onto 2d screen surface
        projected = matmul(projection, transformed)

        px = projected[0][0]
        py = projected[1][0]
        # transform 2d matrix into list
        drawpoint = [int(projected[0][0]), int(projected[1][0])]
        # center on the screen
        offx = screenW/2
        offy = screenH/2
        drawpoint[0] += int(offx)
        drawpoint[1] += int(offy)
        projectedPoints.append(drawpoint)


        # could render right here but i choose to render them in a sep
        # loop not mixed with all the transformations

    # test render the plane?
    # whats awkward about this is that one plane always renders on top the other despite it being "behind it" in the projection
    #pygame.draw.polygon(screen, (0, 255, 255), [projectedPoints[0], projectedPoints[1], projectedPoints[2], projectedPoints[3]], 0)
    #pygame.draw.polygon(screen, (255, 255, 0), [projectedPoints[4], projectedPoints[5], projectedPoints[6], projectedPoints[7]], 0)

    # RENDER THEM OUT
    for drawpoint in projectedPoints:
        # offset the point to the center of the camera for better viewing
        #offx = 1280/2
        #offy = 720/2
        #drawpoint[0] += int(offx)
        #drawpoint[1] += int(offy)

        # draw point
        pygame.draw.circle(screen, (255, 0, 255), drawpoint, 2)

    pygame.display.flip()
    # /// DRAW END

while True:

    inputlisten()

    update()

    draw()

    time.sleep(1 / 60)
