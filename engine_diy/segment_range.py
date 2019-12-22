
class SegmentNode(object):
    def __init__(self):
        self.range = None
        self.previous = None
        self.next = None
    def setRange(self, x1, x2):
        self.range = SolidSegmentRange(x1, x2)
    def insertPrevious(self, x1, x2):
        p = self.previous
        self.previous = SegmentNode()
        self.previous.setRange(x1, x2)
        self.previous.next = self
        self.previous.previous = p
        return self.previous
    def insertNext(self, x1, x2):
        n = self.next
        self.next = SegmentNode()
        self.next.setRange(x1, x2)
        self.next.previous = self
        self.next.next = n
        return self.next
    def __str__(self):
        # recurses
        if self.next != None:
            return "{},{} > {}".format(self.range.xStart, self.range.xEnd, self.next)
        return "{},{}".format(self.range.xStart, self.range.xEnd)

class SolidSegmentRange(object):
    def __init__(self, x1, x2):
        self.xStart = x1
        self.xEnd = x2
    def __str__(self):
        return "{},{}".format(self.xStart, self.xEnd)


