from engine import linedef
from engine import display

class SolidBSPNode(object):
    def __init__(self, lineDefs):
        self.splitter = None # LineDef
        self.front = None # Self
        self.back =  None # Self
        self.isLeaf = False
        self.isSolid = False

        if len(lineDefs) == 0: # leaf
            return

        # get splitter line
        splitterIndex = self.selectBestSplitter(lineDefs)
        self.splitter = lineDefs[splitterIndex]

        # iterate the lineDefs and figure out which side of the splitter they are on
        frontList = []
        backList = []
        for lineDef in lineDefs:
            # skip splitter self check
            if lineDef != self.splitter:
                d = self.classifyLine(self.splitter, lineDef)
                
                if d == 1:
                    # Behind
                    backList.append(lineDef)
                elif d == 2 or d == 4:
                    # Front or coplanar
                    frontList.append(lineDef)
                elif d == 3:
                    # Spanning
                    # first element is behind, second is in front
                    splits = self.splitLine(self.splitter, lineDef)
                    backList.append(splits[0])
                    frontList.append(splits[1])
        
        # all lines have been split and put into front or back list
        if len(frontList) == 0:
            # create an empty leaf node
            self.front = SolidBSPNode([])
            self.front.isLeaf = True
            self.front.isSolid = False
        else:
            # create our recursive front
            self.front = SolidBSPNode(frontList)
        
        if len(backList) == 0:
            # create a solid back node
            self.back = SolidBSPNode([])
            self.back.isLeaf = True
            self.back.isSolid = True
        else:
            # create our recursive back
            self.back = SolidBSPNode(backList)

    def splitLine(self, splitterLineDef, lineDef):
        # first element is behind, second is in front, use facing from parent
        splits = splitterLineDef.split(lineDef)

        splitBehind = splits[0]
        splitBehindDef = linedef.LineDef()
        splitBehindDef.asRoot(splitBehind[0][0], splitBehind[0][1], splitBehind[1][0], splitBehind[1][1], lineDef.facing,  lineDef.height)

        splitFront = splits[1]
        splitFrontDef = linedef.LineDef()
        splitFrontDef.asRoot(splitFront[0][0], splitFront[0][1], splitFront[1][0], splitFront[1][1], lineDef.facing,  lineDef.height)
        return [splitBehindDef, splitFrontDef]

    # if all points behind, we would put whole poly in back list
    # if all points ahead, we would put whole poly in front list
    # if overlap, split and put into both
    def classifyLine(self, splitterLineDef, lineDef):
        return splitterLineDef.classifyLine(lineDef)

    def selectBestSplitter(self, lineDefs):
        # compare each line to each other line
        # classify where the line falls and increment number
        best = 99999
        splitterIndex = 0
        for idxA, lineDefA, in enumerate(lineDefs):
            fronts = 0
            backs = 0
            splits = 0
            for idxB, lineDefB, in enumerate(lineDefs):
                if lineDefA != lineDefB:
                    d = self.classifyLine(lineDefA, lineDefB)
                    if d == 1: #back
                        backs += 1
                    elif d == 2 or d == 4: # front or coplanar
                        fronts += 1
                    elif d == 3: # spanning
                        splits += 1
                    # make splits more costly
                    score = abs(fronts - backs) + (splits * 8)
                    if score < best:
                        best = score
                        splitterIndex = idxA
        return splitterIndex

    def inEmpty(self, testPoint):
        # recurse the tree until we find a leaf node
        if self.isLeaf:
            return self.isSolid == False
        beh = self.splitter.isPointBehind(testPoint[0], testPoint[1])
        if beh:
            return self.back.inEmpty(testPoint)
        else:
            return self.front.inEmpty(testPoint)

    def getWallsSorted(self, posA, posB, walls, depth = 0):
        if not self.isLeaf:
            behind = self.splitter.isPointBehind(posA, posB)
            # painter's algorithm paints back to front, (front to back recursively)
            # to switch to doom algorithm (requires clipping) swap front and back orders
            if behind:
                self.front.getWallsSorted(posA, posB, walls, depth + 1)
                # walls.append(self.splitter)
                self.back.getWallsSorted(posA, posB, walls, depth + 1)
            else:
                self.back.getWallsSorted(posA, posB, walls, depth + 1)
                walls.append(self.splitter)
                self.front.getWallsSorted(posA, posB, walls, depth + 1)

    def drawWalls(self, camera, display, depth = 0):
        if self.isLeaf == False:
            behind = self.splitter.isPointBehind(camera.worldX, camera.worldY)
            if not behind:
                topLeft, topRight, bottomRight, bottomLeft = camera.projectWall(self.splitter, display.width, display.height)
                if topLeft:
                    wallLines = [ topLeft, topRight, bottomRight, bottomLeft ]
                    display.drawPolygon(wallLines, self.splitter.drawColor, 0)
        if self.front:
            self.front.drawWalls(camera, display, depth + 1)
        if self.back:
            self.back.drawWalls(camera, display, depth + 1)

    def drawSegs(self, display, depth = 0):
        # draw self
        if self.isLeaf == False:
            
            ln = 4
            mx = self.splitter.mid[0]
            my = self.splitter.mid[1]
            nx = self.splitter.normals[self.splitter.facing][0] * ln
            ny = self.splitter.normals[self.splitter.facing][1] * ln
            if self.splitter.facing == 1:
                display.drawLine([ [mx, my] , [mx + nx, my + ny] ], (0, 255, 255), 1)
            else:
                display.drawLine([ [mx, my] , [mx + nx, my + ny] ], (255, 0, 255), 1)
            
            display.drawLine([self.splitter.start, self.splitter.end], self.splitter.drawColor, 1)

        if self.back:
            self.back.drawSegs(display, depth + 1)
        if self.front:
            self.front.drawSegs(display, depth + 1)

    def drawFaces(self, display, posA, posB, depth = 0):
        # draw self
        if self.isLeaf == False:
            behind = self.splitter.isPointBehind(posA, posB)
            if not behind:
                display.drawLine([self.splitter.start, self.splitter.end], (255, depth * 20, 0), 1)
            else:
                display.drawLine([self.splitter.start, self.splitter.end], (60, depth * 5, 0), 1)

        if self.back:
            self.back.drawFaces(display, posA, posB, depth + 1)
        if self.front:
            self.front.drawFaces(display, posA, posB, depth + 1)


    def toText(self, depth = 0):
        s = "{}\n".format(self)
        if self.back:
            s += "{}BACK {}: {}".format(" " * (depth+1), depth, self.back.toText(depth+1))
        if self.front:
            s += "{}FRNT {}: {}".format(" " * (depth+1), depth, self.front.toText(depth+1))
        return s

    def __str__(self):
        if self.splitter:
            return "splitter: {}".format(self.splitter)
        else:
            return "isLeaf: {} - isSolid: {}".format(self.isLeaf, self.isSolid)


