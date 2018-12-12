class BSP:
    def __init__(self, lineDefs):
        # Pick a splitter
        self.spitterIndex = 0 # todo make this random or something
        self.splitterLineDef = lineDefs[self.spitterIndex]

        # look at all other lines and determine if they are in front or behind
        for idx, val in enumerate(lineDefs):
            if idx == self.spitterIndex:
                continue
            print(idx, val)
