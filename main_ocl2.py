import pygame, engine_ocl, math, time
from engine_ocl.display import Display
from engine_ocl.eventlistener import EventListener

class Vector3(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    def clone(self):
        return Vector3(self.x, self.y, self.z)
    def __str__(self):
        return "Vector3(" +str(self.x) + "," + str(self.y) + "," + str(self.z) + ")"
    def __repr__(self):
        return self.__str__()

class Triangle(object):
    def __init__(self):
        self.points = [None, None, None] # 3 Vector3s
    def clone(self):
        c = Triangle()
        for i, p in enumerate(self.points):
            c.points[i] = p.clone()
        return c
    @classmethod
    def withPointList(cls, pl):
        t = cls()
        t.points = [Vector3(pl[0], pl[1], pl[2]), Vector3(pl[3], pl[4], pl[5]), Vector3(pl[6], pl[7], pl[8])]
        return t

class Mesh(object):
    def __init__(self):
        self.triangles = []


# START GAME

display = Display(640, 480)
listener = EventListener()
#pygame.mouse.set_visible(False)
#pygame.event.set_grab(True)

# OCL 1 was about creating the Perspective Matrix
# OCL 2 is  other stuff, see OCL1 for more notes

# OCL PART 1
# PERSPECTIVE PROJECTION
#
#
# 1. Establish X and Y Scaling Coefficients
#
# Normalize Screen space: -1 to +1 for width and height, 0,0 at center
#
# Human eye projects things in a field of view being -1, +1 at any position
# Objects closer to eye take up more of the field of view
# -1 and +1 act as clipping values, anything outside this range is out of our FoV
#    _________
# -1 \       / +1
#     \     /
#   -1 \___/ +1
#        * eye
#
# If we zoom in (narrow) the FoV we see less, but its larger
# If we zoom out (exand) the FoV we see more, but things are smaller
# We create a Scaling Factor related to the FoV we will call Theta: θ
# -1 \       / +1
#     \_---_/
#   -1 \_θ_/ +1
#
# We can think of theta in 2 right angles, as theta/2
#    _________
# -1 \  ∟|   / +1
#     \  |  /
#   -1 \_|_/ +1
#        θ/2
# When theta/2 increases (our FoV increases) and the opposite side increases
#           ______ < (increases)
# -1 \    ∟|     / +1
#      \   |   /
#   -1   \_|_/ +1
#        θ/2
# If we scale things by tan(theta/2) then it will displace things larger as the FoV increases
# So instead we need to scale by its inverse 1/tan(theta/2)
# Projection
# [x,y,z] = [ (h/w) fx, fy, z ]
# where f = 1/tan(theta/2)
#
#
# 2. Establish Z Scaling Coefficient
#
# Calculating Zed scaling coefficient within a projection zone (frustrum?)
# e.g
#    _________ zfar = 10
#    \       /
#     \     /
#      \___/ znear = 1
#        * eye
# We need to normalize our z coord within our projection space
# This is equal to dividing z by the size of the space: z / (zfar - znear) to get it to 0 to 1
# But we must also scale it up to our overall range so: z * zfar / (zfar - znear)
# This makes zfar / (zfar - znear) our scaling factor
# But scaling z by this alone is not enough, we need to offset by the distance from the eye
# So we need to offset by znear also normalized and scaled: - znear * zfar / (zfar - znear)
# So the final coefficient is z * (zfar / (zfar - znear)) - (znear * zfar / (zfar - znear))
#
# This leaves us with a perspective projection of
# [x,y,z] = [ (h/w) * (1/tan(theta/2)) * x,
#             (1/tan(theta/2)) * y,
#             z * (zfar / (zfar - znear)) - (znear * zfar / (zfar - znear)) ]
#
# When things move away they appear smaller
# As Z gets larger (further from screen) both X and Y get smaller (they shrink away)
# x' = x/z   y' = y/z
#
# This leave us with a perspective projection of
# [x,y,z] = [ (h/w) * (1/tan(theta/2)) * x / z,
#             (1/tan(theta/2)) * y / z,
#             z * (zfar / (zfar - znear)) - (znear * zfar / (zfar - znear)) ]
#                                                   ^
# Lets simplify, let                                  \
# a = (h/w)                   aspect ratio               \
# f = (1/tan(theta/2))        field of view                 \
# q = zfar / (zfar - znear)   zed normalization  (which is within this formula too)
# becomes
# [x,y,z] = [ a*f*x / z, f*y / z, z*q - znear*q ]
#
#
# 3. Mathematically Apply Coeffecients with a 4x4 Matrix
#
# Instead of coding these directly lets use Matrix mathematics to do our multiplications
# [x, y, z] dot [   af    0    0   ] = [afx, fy, qz] !BUT we are missing our - znear*q!
#               [   0     f    0   ]                 !We are also missing our divide by z
#               [   0     0    q   ]
#
# Since dot product is a sum of the row * col we can add a 4th item on row 3 to get added
# to the overall value of the z position
# [x, y, z] dot [   af    0    0   ]
#               [   0     f    0   ]
#               [   0     0    q   ]
#               [           -zn*q  ]
# But this requires it to be a 4x4 vector, so we must extend our input vector with a "1"
# [x, y, z, 1] dot [   af   0    0   ? ] = [afx, fy, qz - znear*q]
#                  [   0    f    0   ? ]
#                  [   0    0    q   ? ]
#                  [   0    0 -zn*q  ? ]
# But we also need to divide by z across x and y so we don't want to lose it in our values
# so we use the fourth column as a trick to save Z for later division as the 4th component
# [x, y, z, 1] dot [   af   0    0   0 ] = [afx, fy, qz - znear*q, z]
#                  [   0    f    0   0 ]
#                  [   0    0    q   1 ]
#                  [   0    0 -zn*q  0 ]
#
# 4. Normalize by Z
#
# After the final vecor is calulated we divide all three coordinates by za
#
# [afx, fy, qz - znear*q, z] => [afx / z, fy / z, (qz - znear*q) / z, z]
#
# ** BUT WHY would we divide  (qz - znear*q) / z ?
# I believe we established that x and y grow inversly to z and technically
# (z*q - znear*q) / z is different than z * (q - znear*q) /z (wrong!)
#
# Reading around I believe its because we are in fact normalizing all three
# coordinates the same way, giving us consistent normalized values in Z space
#
#
# At this point we have a scaling matrix for perspective projection,
# what we do not have is clipping outside of the FoV or hiding faces
# that face away from us



# OCL PART 2
#
# 1. Determining a Plane's normal
# Hiding polygon faces that face away from the camera
# Because all triangles are "wound" the same direction we can
# calculate their normals to determine what way they "face"
# the winding direction determining which side is "out"
#
# The Cross Product will produce the Normal of a plane
# the line that is perpendiculat to the two lines provided
#
# Cross Product:
# Nx = Ay * Bz - Az * By
# Ny = Az * Bx - Ax * Bz
# Nz = Ax * By - Ay * Bx
#
# If we have a triangle wound clockwise we can take:
# Point 1 - Point 0 to be Line A
# Point 2 - Point 0 to be Line B
# Crossing that produces the normal of Point 0
# If we wound counter-clockwise the normal would be in the opposite direction
#
# Most importantly is that all triangles are order in the same way!!
#
#
# 2. Determining if a Face is Away from Camera
# If Z positive is away from the camera, any faces with a Normal Positive are facing away
#
# We calculate the normals of the lines of the triangle
# We then calculate the length of the normal and normalize itself with pythagoreum eg:
# normalLen = math.sqrt(normal.x * normal.x + normal.y * normal.y + normal.z * normal.z) # pythagoreum
# normal.x /= normalLen; y... z... etc
# Then if normal.z is less than 0 we hide it.
#
# However!! If we do this it will hide faces that are orthogonally facing away from the origin of the worl
# which misses two main parts:
# 1. It does not capture perspective and this faces that are somewhat "away" from us still appear
#    because orthogonally they are visible or at normal.z = 0, but in perspective they are away from us
# 2. It does not account for a camera that may "move" or have a non-origin position
#
# Instead of looking at Z alone we need to look at it in relation to the camera line from the camera position
# to the points location in 3D
# IE the alignment of the Z normal in regards to the line from the camera to the point
# So if we form the two lines and determine the angle between them, anything greater than 90deg is hidden
#
# Welcome Dot Product
# D = Ax*Bx + Ay*By + Az*BZ
# This gets us how much the line projects onto the other line (if they are normalized with the same value)
# If the Dot product is 0, they dont project at all (ie 90deg)
# If nonzero, then it project in one way or another
# Example:
# A = (1,0,0), B = (0,1,0) => 1*0 + 0*1 + 0*0 = 0+0+0 = 0 // all zero and vectors do not cross anywhere, orthogonal
# A = (1,0,0), B = (1,0,0) => 1*1 + 0*0 + 0*0 = +1        // exactly the same
# A = (1,0,0), B = (-1,0,0) => 1*-1 + 0*0 + 0*0 = -1      // B is exact opposite direction
#
# We also want to offset by our camera position too, but ultimately it looks like this:
#
# if (normal.x * (planePoint.x - camera.x) + normal.y * (planePoint.y - camera.y) + normal.z * (planePoint.z - camera.z) < 0
#   then hide the face






def deg2rad(v):
    return v / 180.0 * 3.14159

# We will create a matrix to hold our stuff
class Matrix4x4(object):
    def __init__(self):
        # rows by cols
        self.m = [[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]] # identity
        #self.m = [[0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0]]

def MultiplyMatrixVector(v3, m):
    v3output = Vector3(0,0,0)
    # the Vector3 does not have a 4th component so we substite 1 for it by just adding the final component
    v3output.x = v3.x * m.m[0][0] + v3.y * m.m[1][0] + v3.z * m.m[2][0] + m.m[3][0] # <<----------/ e.g.
    v3output.y = v3.x * m.m[0][1] + v3.y * m.m[1][1] + v3.z * m.m[2][1] + m.m[3][1]
    v3output.z = v3.x * m.m[0][2] + v3.y * m.m[1][2] + v3.z * m.m[2][2] + m.m[3][2]
    w = v3.x * m.m[0][3] + v3.y * m.m[1][3] + v3.z * m.m[2][3] + m.m[3][3]

    if w != 0.0: # divide by our original "z" to normalize our values
        v3output.x /= w
        v3output.y /= w
        v3output.z /= w

    return v3output

# Perspective Projection matrix for camera
zNear = 0.1
zFar = 1000.0
fov = 90
aspectRatio = display.aspectRatio
fovRad = 1.0 / math.tan(deg2rad(fov / 2)) # convert to radians

# [   af   0    0   0 ]
# [   0    f    0   0 ]
# [   0    0    q   1 ]
# [   0    0 -zn*q  0 ]
projectionMatrix = Matrix4x4() # rows, cols
projectionMatrix.m[0][0] = aspectRatio * fovRad
projectionMatrix.m[1][1] = fovRad
projectionMatrix.m[2][2] = zFar / (zFar - zNear)
projectionMatrix.m[3][2] = (-zNear * zFar) / (zFar - zNear)
projectionMatrix.m[2][3] = 1.0
projectionMatrix.m[3][3] = 0.0 # replace 1 in identity matrix
# Go to game loop to see projection being used


# define triangle points in clockwise direction for a cube
# south
t1  = Triangle.withPointList([0,0,0, 0,1,0, 1,1,0])
t2  = Triangle.withPointList([0,0,0, 1,1,0, 1,0,0])
# east
t3  = Triangle.withPointList([1,0,0, 1,1,0, 1,1,1])
t4  = Triangle.withPointList([1,0,0, 1,1,1, 1,0,1])
# north
t5  = Triangle.withPointList([1,0,1, 1,1,1, 0,1,1])
t6  = Triangle.withPointList([1,0,1, 0,1,1, 0,0,1])
# west
t7  = Triangle.withPointList([0,0,1, 0,1,1, 0,1,0])
t8  = Triangle.withPointList([0,0,1, 0,1,0, 0,0,0])
# top
t9  = Triangle.withPointList([0,1,0, 0,1,1, 1,1,1])
t10 = Triangle.withPointList([0,1,0, 1,1,1, 1,1,0])
# bottom
t11 = Triangle.withPointList([1,0,1, 0,0,1, 0,0,0])
t12 = Triangle.withPointList([1,0,1, 0,0,0, 1,0,0])

mesh = Mesh()
mesh.triangles.append(t1)
mesh.triangles.append(t2)
mesh.triangles.append(t3)
mesh.triangles.append(t4)
mesh.triangles.append(t5)
mesh.triangles.append(t6)
mesh.triangles.append(t7)
mesh.triangles.append(t8)
mesh.triangles.append(t9)
mesh.triangles.append(t10)
mesh.triangles.append(t11)
mesh.triangles.append(t12)

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
titletext = font.render("Perspective Projection of a rotating cube", 1, (50, 50, 50));
textpos = titletext.get_rect(bottom = display.height - 10, centerx = display.width/2)


timeLapsed = 0
while True:

    listener.update()
    display.start()

    display.drawText(titletext, textpos)

    # hardcoded rotation matrices
    # rotate around Z with time
    matRotZ = Matrix4x4()
    matRotZ.m[0][0] = math.cos(timeLapsed)
    matRotZ.m[0][1] = math.sin(timeLapsed)
    matRotZ.m[1][0] = -math.sin(timeLapsed)
    matRotZ.m[1][1] = math.cos(timeLapsed)
    matRotZ.m[2][2] = 1
    matRotZ.m[3][3] = 1

    # rotate around X with half/time
    matRotX = Matrix4x4()
    matRotX.m[0][0] = 1
    matRotX.m[1][1] = math.cos(timeLapsed / 2)
    matRotX.m[1][2] = math.sin(timeLapsed / 2)
    matRotX.m[2][1] = -math.sin(timeLapsed / 2)
    matRotX.m[2][2] = math.cos(timeLapsed / 2)
    matRotX.m[3][3] = 1

    # Draw triangles projected into our perspective
    for t in mesh.triangles:

        # 1. Rotation Visualization Helper
        # So we can see if its actually a cube lets rotate it about its
        # x and z axis to see it
        # Rotation comes before translation since we rotate around origin
        # lets use our total elapsed time to rotate with
        # lets hardcode two rotation matrices
        # (since these are static we moved them out of the loop above)

        # rotate in z
        rotZPoint0 = MultiplyMatrixVector(t.points[0], matRotZ)
        rotZPoint1 = MultiplyMatrixVector(t.points[1], matRotZ)
        rotZPoint2 = MultiplyMatrixVector(t.points[2], matRotZ)
        rotZPoints = [rotZPoint0, rotZPoint1, rotZPoint2]

        # rotate in x
        rotZXPoint0 = MultiplyMatrixVector(rotZPoints[0], matRotX)
        rotZXPoint1 = MultiplyMatrixVector(rotZPoints[1], matRotX)
        rotZXPoint2 = MultiplyMatrixVector(rotZPoints[2], matRotX)
        rotZXPoints = [rotZXPoint0, rotZXPoint1, rotZXPoint2]

        # 2. Translation Visualization Helper
        # Currently our cube is centered around 0-1 ranges, so our head is
        # essentially aligned with the front of the cobe
        # Translate triangle away from camera by adding to z to push it away
        triTransPoints = rotZXPoints
        triTransPoints[0].z += 3.0
        triTransPoints[1].z += 3.0
        triTransPoints[2].z += 3.0

        # 3. Calculate Normal hide those facing away
        line1 = Vector3(
            triTransPoints[1].x - triTransPoints[0].x,
            triTransPoints[1].y - triTransPoints[0].y,
            triTransPoints[1].z - triTransPoints[0].z
        )
        line2 = Vector3(
            triTransPoints[2].x - triTransPoints[0].x,
            triTransPoints[2].y - triTransPoints[0].y,
            triTransPoints[2].z - triTransPoints[0].z
        )
        # directly implement cross product of the lines
        normal = Vector3(
            line1.y * line2.z - line1.z * line2.y,
            line1.z * line2.x - line1.x * line2.z,
            line1.x * line2.y - line1.y * line2.x,
        )
        # calculate normal of normal vector so we can normalize things....
        normalLen = math.sqrt(normal.x * normal.x + normal.y * normal.y + normal.z * normal.z) # pythagoreum
        normal.x /= normalLen
        normal.y /= normalLen
        normal.z /= normalLen

        # if normal is facing away from camera then hide it
        # if (normal.z < 0): This method does not work it only hides faces in regards to origin of world and without camera offset
        # instead we calculate Dot product of normal vector and the plane position in relation to the camera (which is a vector)
        # note, we can pick any point on the triangle since its a plane
        if (normal.x * (triTransPoints[0].x - tempCamera.x) +
            normal.y * (triTransPoints[0].y - tempCamera.y) +
            normal.z * (triTransPoints[0].z - tempCamera.z) < 0):

            # Lets add some lighting for the triangle since its not culled
            lightDir = Vector3(0, 0, -1) # create a light coming out of the camera
            lightLen = math.sqrt(lightDir.x * lightDir.x + lightDir.y * lightDir.y + lightDir.z * lightDir.z)
            lightDir.x /= lightLen; lightDir.y /= lightLen; lightDir.z /= lightLen # normalize it
            # get Dot Product of light with Normal
            # the floating point value of this is how aligned they are, so 1 == perfectly aligned
            dot = normal.x * lightDir.x + normal.y * lightDir.y + normal.z * lightDir.z
            # lets shade a color by this amount
            color = (int(255.0 * dot), int(255.0 * dot), 0)


            # 4. Project our points to our perspective from World Space to Screen Space
            projPoint0 = MultiplyMatrixVector(triTransPoints[0], projectionMatrix)
            projPoint1 = MultiplyMatrixVector(triTransPoints[1], projectionMatrix)
            projPoint2 = MultiplyMatrixVector(triTransPoints[2], projectionMatrix)
            projPoints = [projPoint0, projPoint1, projPoint2]

            # 5. Scale into viewport
            # points between -1 and -1 are within our screens FoV
            # so we want something at 0,0 to be at the center of the view, -1,0 at left, 0,1 at bottom etc
            # start by shifting the normalized x,y points to the range 0-2
            projPoints[0].x += 1.0; projPoints[0].y += 1.0
            projPoints[1].x += 1.0; projPoints[1].y += 1.0
            projPoints[2].x += 1.0; projPoints[2].y += 1.0
            # divide the points by 2 and then multiply by size of screen
            # so something at -1 becomes 0/2=0 (left side) and +1 becomes 2/2=1 (right side)
            # something at 1 then becomes the size of the screen
            projPoints[0].x *= .5 * display.width; projPoints[0].y *= .5 * display.height
            projPoints[1].x *= .5 * display.width; projPoints[1].y *= .5 * display.height
            projPoints[2].x *= .5 * display.width; projPoints[2].y *= .5 * display.height

            # 6. Draw
            fillTriangle(display, projPoints, color);
            drawTriangle(display, projPoints, (0,0,0), 1)

    display.end()

    time.sleep(1 / 60)
    timeLapsed += (1 / 60)
