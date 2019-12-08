import sys, pygame, math, time

# matrix is array of array
# vec3 is an array of array pairs [[x,y], ...]
# same as dot product
# Two vectors multiplied together and summed to produce a scalar
# Each element in the same row multiplied together. The result of each row added together
# [2] . [-1] =  ((2 * -1) + (3 * 5)) = 13
# [3]   [ 5]
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

pygame.init()
screen = pygame.display.set_mode((1280, 720), 0, 32)

cameraX = 0
cameraY = 0
cameraZ = 0
cameraAngleX = 0.0
cameraAngleY = 0.0
cameraAngleZ = 0.0

# DEFINE OUR PLANE IN 3D SPACE
a3 = [-1, -1, -1]
b3 = [ 1, -1, -1]
c3 = [ 1,  1, -1]
d3 = [-1,  1, -1]

e3 = [-1, -1, 1]
f3 = [ 1, -1, 1]
g3 = [ 1,  1, 1]
h3 = [-1,  1, 1]
points = [a3, b3, c3, d3,   e3, f3, g3, h3] # two sides of cube

angleX = 0.4 # of cube
angleY = 0.0
angleZ = 0.0

while True:

    # LOOP START
    screen.fill((200, 200, 200))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                sys.exit(0)


    angleX += 0.00
    angleY += 0.01
    angleZ += 0.00

    # CALCULATE CAMERA TRANSFORM MATRIX
    identity = [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ]

    # REPOSITION AND PROJECT EACH POINT
    projectedPoints = []
    for i in range(len(points)):

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
        # TODO: all of this is transformation of our cube model
        # and could be put in a model class

        # SCALE OUR POINT
        # I defined the model in unit space and
        # need to scale the model to world space
        scaleX = 100
        scaleY = 100
        scaleZ = 100
        scale = [
            [scaleX, 0, 0, 0],
            [0, scaleY, 0, 0],
            [0, 0, scaleZ, 0],
            [0, 0, 0, 1]
        ]
        transform = scale

        # ROTATE THE POINT IN 3D SPACE
        # we can calculate the rotation in each axis
        # based on whatever the angle for that axis is
        rotationX = [
            [1, 0, 0, 0],
            [0, math.cos(angleX), - math.sin(angleX), 0],
            [0, math.sin(angleX),   math.cos(angleX), 0],
            [0, 0, 0, 1]
        ]
        rotationY = [
            [math.cos(angleY), 0, - math.sin(angleY), 0],
            [0, 1, 0, 0],
            [math.sin(angleY), 0,   math.cos(angleY), 0],
            [0, 0, 0, 1]
        ]
        rotationZ = [
            [math.cos(angleZ), - math.sin(angleZ), 0, 0],
            [math.sin(angleZ),   math.cos(angleZ), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ]
        transform = matmul(rotationX, transform)
        transform = matmul(rotationY, transform)
        transform = matmul(rotationZ, transform)

        # TRANSLATE FROM MODEL SPACE (-1, 1) TO WORLD SPACE
        # keeping the points in model space around the
        # model's origin, we can give the whole cube a
        # world position and translate our model to that
        # position by placing its world position in the
        # final column for x, y, z
        worldX = 100
        worldY = 0
        worldZ = 0
        translation = [
            [1, 0, 0, worldX],
            [0, 1, 0, worldY],
            [0, 0, 1, worldZ],
            [0, 0, 0, 1]
        ]
        transform = matmul(translation, transform)

        # MULTIPLY TRANSFORMATION MATRIX TO POSITION
        # convert vector3 into a 1col matrix
        p = [[points[i][0]], [points[i][1]], [points[i][2]], [1]]
        transformed = matmul(transform, p)


        # V
        # DETERMINE VIEW TRANSFORMATION MATRIX
        # basically move everything in the world
        # to be positioned relative to the camera

        # P
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
        z = 1 / -transformed[2][0];
        #z = 1 / (distance - rotated[2][0])
        perspectiveProjection = [
            [z, 0, 0, 0],
            [0, z, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ]

        #projection = perspectiveProjection
        projection = orthographicProjection

        # project onto 2d screen surface
        projected = matmul(projection, transformed)

        # transform 2d matrix into list
        drawpoint = [int(projected[0][0]), int(projected[1][0])]

        # center on the screen
        offx = 1280/2
        offy = 720/2
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


    # LOOP END
    pygame.display.flip()

    time.sleep(1 / 60)
