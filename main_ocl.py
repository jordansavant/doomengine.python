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
