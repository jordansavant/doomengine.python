import sys, pygame, engine, math, time

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

a = (-100, -100)
b = ( 100, -100)
c = ( 100,  100)
d = (-100,  100)

# DEFINE OUR PLANE IN 3D SPACE
a3 = [-100, -100, -100]
b3 = [ 100, -100, -100]
c3 = [ 100,  100, -100]
d3 = [-100,  100, -100]

points = [a3, b3, c3, d3]

angle = 0.0

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

    # CALCULATE PROJECTION MATRIX
    # ortho?
    projection = [
        [1, 0, 0],
        [0, 1, 0]
    ]

    # CALCULATION ROTATION MATRICES
    rotationX = [
        [1, 0, 0],
        [0, math.cos(angle), - math.sin(angle)],
        [0, math.sin(angle),   math.cos(angle)]
    ]
    rotationY = [
        [math.cos(angle), 0, - math.sin(angle)],
        [0, 1, 0],
        [math.sin(angle), 0,   math.cos(angle)]
    ]
    rotationZ = [
        [math.cos(angle), - math.sin(angle), 0],
        [math.sin(angle),   math.cos(angle), 0],
        [0, 0, 1]
    ]

    # ROTATE THE POINTS
    #pygame.draw.polygon(screen, (0, 255, 255), (a, b, c, d), 0)

    # REPOSITION AND PROJECT EACH POINT
    projectedPoints = []
    for i in range(len(points)):

        # transform vector3 into a 1col matrix
        p = [[points[i][0]], [points[i][1]], [points[i][2]]]
        # rotate the point in 3d space
        rotated = matmul(rotationX, p)
        rotated = matmul(rotationY, rotated)
        rotated = matmul(rotationZ, rotated)
        # project onto 2d screen surface
        projected = matmul(projection, rotated)

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
    pygame.draw.polygon(screen, (0, 255, 255), projectedPoints, 0)

    # RENDER THEM OUT
    for drawpoint in projectedPoints:
        # offset the point to the center of the camera for better viewing
        #offx = 1280/2
        #offy = 720/2
        #drawpoint[0] += int(offx)
        #drawpoint[1] += int(offy)

        # draw point
        pygame.draw.circle(screen, (255, 0, 255), drawpoint, 5)


    angle += 0.03

    # LOOP END
    pygame.display.flip()

    time.sleep(1 / 60)
