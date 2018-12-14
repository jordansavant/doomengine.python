class SolidBSPNode(object):
    def __init__(self, lineDefs):
        self.splitter = None # LineDef
        self.splitterIndex = None
        self.front = None # Self
        self.back =  None # Self
        self.isLeaf = False
        self.isSolid = False

        if len(lineDefs) == 0: # leaf
            return

        # get splitter line
        self.splitterIndex = self.selectBestSplitter(lineDefs)
        self.splitter = lineDefs[self.splitterIndex]

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
                elif d == 2:
                    # Front
                    frontList.append(lineDef)
                elif d == 3:
                    # Same Plane
                    frontList.append(lineDef)
                else:
                    # Spanning
                    splits = self.splitLine(self.splitter, lineDef)
                    frontList.append(splits.front)
                    backList.append(splits.back)
        
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
        # TODO, make this a thing
        return {
            front: None,#TODO,
            back: None#TODO
        }
    
    def classifyLine(self, splitterLineDef, lineDef):
        # 1 = back
        # 2 = front
        # 3 = co planar
        # 4 = spanning
        # TODO: complete
        return 1

    def selectBestSplitter(self, lineDefs):
        # TODO, make this smarter
        return 0

    def render(self, depth = 0):
        s = "{}{}".format(" " * depth, self)
        if self.back:
            s += "{}BACK {}: {}".format(" " * depth, depth, self.back.render(depth+1))
        if self.front:
            s += "{}FRNT {}: {}".format(" " * depth, depth, self.front.render(depth+1))
        return s

    def __str__(self):
        if self.splitter:
            return "isLeaf: {} - isSolid: {} - splitter: {}, {}\n".format(
                self.isLeaf, self.isSolid, self.splitter.start, self.splitter.end
            )
        else:
            return "isLeaf: {} - isSolid: {}\n".format(
                self.isLeaf, self.isSolid
            )


