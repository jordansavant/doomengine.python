import pygame, engine_ocl, math, time
from engine.display import Display
from engine.eventlistener import EventListener

class Vector3(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Triangle(object):
    def __init__(self):
        self.points = [None, None, None] # 3 Vector3s
    @classmethod
    def withPointList(cls, pl):
        t = cls()
        t.points = [Vector3(pl[0], pl[1], pl[2]), Vector3(pl[3], pl[4], pl[5]), Vector3(pl[6], pl[7], pl[8])]
        return t

class Mesh(object):
    def __init__(self):
        self.triangles = []


# START GAME

display = Display(1920, 1080)
listener = EventListener()
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)
font = pygame.font.Font(None, 36)


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
# Calculating Zed within a projection zone (frustrum?)
# e.g
#    _________ zfar = 10
#    \       /
#     \     /
#      \___/ znear = 1
#        * eye
# zfar - znear = 9
# if we want to find our z wihin the frustrum we must scale
# zfar / (zfar - znear)
# then we must offset by our offset of the frustrum from the eye
# final:
# (zfar / (zfar - znear)) - (zfar * znear / (zfar - znear))
#
# This leaves us with a final transformation projection of
# [x,y,z] = [ (h/w) * (1/tan(theta/2)) * x,
#             (1/tan(theta/2)) * y,
#             zfar / (zfar - znear)) - (zfar * znear / (zfar - znear)) *z ]
#
#

# create mesh cube
mesh = Mesh()
# define triangle points in clockwise direction
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
t9  = Triangle.withPointList([0,1,0, 0,0,1, 0,0,0])
t10 = Triangle.withPointList([1,0,1, 0,0,0, 1,0,0])
# bottom
t11 = Triangle.withPointList([1,0,1, 0,0,1, 0,0,0])
t12 = Triangle.withPointList([1,0,1, 0,0,0, 1,0,0])

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

def trans(v): # translate to screen
    return v * 100 + 200

while True:
    listener.update()

    display.start()

    for t in mesh.triangles:
        for i, p in enumerate(t.points):
            if i < 2: # connect to neighbor
                display.drawLine([[trans(p.x), trans(p.y)], [trans(t.points[i+1].x), trans(t.points[i+1].y)]], (255, 255, 0), 1)
            else: # connect to beginning
                display.drawLine([[trans(p.x), trans(p.y)], [trans(t.points[0].x), trans(t.points[0].y)]], (255, 255, 0), 1)

    display.end()

    time.sleep(1 / 60)
