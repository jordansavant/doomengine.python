class PolyDef(object):

    def __init__(self):
        self.lineDefs = []
        self.direction = None # 0 = Clockwise, 1 = CounterClockwise
        return

    def addLineDef(self, lineDef, facing):
        