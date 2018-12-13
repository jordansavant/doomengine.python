# LineDef
# Start, End, Facing Direction

class BSP:
    def __init__(self, lineDefs):
        # Pick a splitter
        self.spitterIndex = 0 # todo make this random or something
        self.splitterLineDef = lineDefs[self.spitterIndex]

        # Build lists
        lineDefsFront = []
        lineDefsBehind = []
        self.nodeFront = None
        self.nodeBehind = None
        self.lineDefsSamePlaneSameFacing = []
        self.lineDefsSamePlaneOppositeFacing = []

        # look at all other lines and determine if they are in front or behind or on the same plane
        for idx, val in enumerate(lineDefs):
            # Don't look at our own splitter
            if idx == self.spitterIndex:
                continue
            print(idx, val)
