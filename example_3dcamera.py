import sys, pygame, engine, math, time

# matrix is array of array
# vec3 is an array of array pairs [[x,y], ...]
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
cameraAngle = 0.0

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

angleX = 0.0 # of cube
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


    # CALCULATION ROTATION MATRICES
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

    # REPOSITION AND PROJECT EACH POINT
    projectedPoints = []
    for i in range(len(points)):

        # TRANSLATE FROM MODEL SPACE (-1, 1) TO WORLD SPACE
        # keeping the points in model space around the
        # model's origin, we can give the whole cube a
        # world position and translate our model to that
        # position by placing its world position in the
        # final column for x, y, z
        worldX = 1
        worldY = 0
        worldZ = 0
        translation = [
            [1, 0, 0, worldX],
            [0, 1, 0, worldY],
            [0, 0, 1, worldZ],
            [0, 0, 0, 1]
        ]

        # ROTATE THE POINT IN 3D SPACE
        # we can calculate the rotation in each axis
        # based on whatever the angle for that axis is
        rotated = translation
        rotated = matmul(rotationX, rotated)
        rotated = matmul(rotationY, rotated)
        rotated = matmul(rotationZ, rotated)

        # APPLY OUR TRANSLATION AND ROTATION MATRIX TO OUR POSITION
        # convert vector3 into a 1col matrix
        p = [[points[i][0] - cameraX], [points[i][1] - cameraY], [points[i][2] - cameraZ], [1]]
        transformed = matmul(rotated, p)

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
        #z = 1 / (distance - rotated[2][0])
        #perspectiveProjection = [
        #    [z, 0, 0],
        #    [0, z, 0]
        #]

        #projection = perspectiveProjection
        projection = orthographicProjection

        # project onto 2d screen surface
        projected = matmul(projection, transformed)

        # transform 2d matrix into list
        zoom = 100
        drawpoint = [int(projected[0][0] * zoom), int(projected[1][0] * zoom)]

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
        pygame.draw.circle(screen, (255, 0, 255), drawpoint, 4)


    # LOOP END
    pygame.display.flip()

    time.sleep(1 / 60)
