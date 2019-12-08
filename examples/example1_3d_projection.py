import sys, pygame, math, time

# matrix is array of array
# vec3 is an array of array pairs [[x,y], ...]
def matmul(matrix, vec3):
    colsA = len(matrix[0])
    colsB = len(vec3[0])
    rowsA = len(matrix)
    rowsB = len(vec3)

    if colsA != rowsB:
        print("matmul mismatch")
        print(matrix, vec3)
        print(colsA, colsB, rowsA, rowsB)
        sys.exit(1)

    r = []
    for j in range(rowsA):
        r.append([])
        for i in range(colsB):
            summ = 0
            for n in range(colsA):
                summ += matrix[j][n] * vec3[n][i]
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
points = [a3, b3, c3, d3]

while True:

    # LOOP START
    screen.fill((200, 200, 200))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                sys.exit(0)


    # LOOP

    # CALCULATION ROTATION MATRICES
    rotationX = [
        [1, 0, 0],
        [0, math.cos(cameraAngle), - math.sin(cameraAngle)],
        [0, math.sin(cameraAngle),   math.cos(cameraAngle)]
    ]
    rotationY = [
        [math.cos(cameraAngle), 0, - math.sin(cameraAngle)],
        [0, 1, 0],
        [math.sin(cameraAngle), 0,   math.cos(cameraAngle)]
    ]
    rotationZ = [
        [math.cos(cameraAngle), - math.sin(cameraAngle), 0],
        [math.sin(cameraAngle),   math.cos(cameraAngle), 0],
        [0, 0, 1]
    ]

    # REPOSITION AND PROJECT EACH POINT
    projectedPoints = []
    for i in range(len(points)):

        # convert vector3 into a 1col matrix
        p = [[points[i][0]], [points[i][1]], [points[i][2]]]

        # TRAN

        # ROTATE THE POINT IN 3D SPACE
        rotated = p
        #rotated = matmul(rotationX, rotated)
        rotated = matmul(rotationY, rotated)
        #rotated = matmul(rotationZ, rotated)

        # CALCULATE PROJECTION MATRIX
        orthographicProjection = [
            [1, 0, 0],
            [0, 1, 0]
        ]
        # reduce x and y when z is further away
        # center of cube is at -z is in front of us (at -1)
        # pushing it away by three lets us see it
        distance = 0.0
        z = 1 / (distance - rotated[2][0])
        perspectiveProjection = [
            [z, 0, 0],
            [0, z, 0]
        ]

        projection = perspectiveProjection
        #projection = orthographicProjection

        # project onto 2d screen surface
        projected = matmul(projection, rotated)

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
    pygame.draw.polygon(screen, (0, 255, 255), projectedPoints, 0)

    # RENDER THEM OUT
    for drawpoint in projectedPoints:
        # offset the point to the center of the camera for better viewing
        #offx = 1280/2
        #offy = 720/2
        #drawpoint[0] += int(offx)
        #drawpoint[1] += int(offy)

        # draw point
        pygame.draw.circle(screen, (255, 0, 255), drawpoint, 2)


    cameraAngle += 0.03

    # LOOP END
    pygame.display.flip()

    time.sleep(1 / 60)
