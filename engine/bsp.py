class SolidBSPNode(object):
    def __init__(self, lineDefs):
        self.splitter = None # LineDef
        self.front = None # Self
        self.back =  None # Self
        self.isLeaf = False
        self.isSolid = False

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
        return 0;

    def __str__(self):
        s = ""
        if self.back:
            s += "\n"
            s += self.back
        if self.front:
            s += "\n"
            s += self.front
        return "self.splitterIndex: {}\nself.isLeaf: {}\nself.isSolid: {}".format(self.splitterIndex, self.isLeaf, self.isSolid)


