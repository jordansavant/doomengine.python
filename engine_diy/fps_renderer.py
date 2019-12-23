import random, math
from engine_diy.player import Player
from engine_diy.angle import Angle
from engine_diy.segment_range import SolidSegmentRange
from engine_diy.map import *

class FpsRenderer(object):
    def __init__(self, map, player, game, fov, width, height, xOffset, yOffset):
        self.map = map
        self.player = player
        self.game = game
        self.fov = fov
        self.width = width
        self.height = height
        self.xOffset = xOffset
        self.yOffset = yOffset

        self.wallColors = {} # helper to map a texture to a single color (until textures are added)
        self.onSegInspect = None # function pointer for helping to visualize segs in fps viewport

        # build lookup table of all x screen coords and
        # their projection angles
        # this was part of the wolfenstein height projection
        self.screenXtoAngleLookup = []
        screenAngle = Angle(fov / 2)
        step = fov / (width + 1) # why +1?
        for i in range(0, width + 1):
            self.screenXtoAngleLookup.append(screenAngle)
            screenAngle.isubF(step)
        self.halfScreenWidth = width / 2
        self.halfScreenHeight = height / 2
        self.halfFov = Angle(fov / 2)
        self.distancePlayerToScreen = self.halfScreenWidth / self.halfFov.getTan() # 160 at 320 width and 90 fov

    def renderEdgesOnly(self, solidOnly = False, onSegInspect = None):
        # loop over all segs
        for i, seg in enumerate(self.map.segs):
            linedef = self.map.linedefs[seg.linedefID]
            # if in mode 8 only render solid walls
            if solidOnly and linedef.isSolid() is False:
                continue

            v1 = self.map.vertices[seg.startVertexID]
            v2 = self.map.vertices[seg.endVertexID]
            angles = self.clipVerticesToFov(v1, v2)
            if angles is not None:
                if onSegInspect is not None:
                    onSegInspect(seg, v1, v2)

                # render fps window for all walls
                v1xScreen = self.angleToScreen(angles[0])
                v2xScreen = self.angleToScreen(angles[1])

                # wall edge1
                fpsStart = [v1xScreen + self.xOffset, self.yOffset]
                fpsEnd = [v1xScreen + self.xOffset, self.height + self.yOffset]
                self.game.drawLine(fpsStart, fpsEnd, (1,1,0,1), 1)

                # wall edge 2
                fpsStart = [v2xScreen + self.xOffset, self.yOffset]
                fpsEnd = [v2xScreen + self.xOffset, self.height + self.yOffset]
                self.game.drawLine(fpsStart, fpsEnd, (1,0,1,1), 1)

    def renderWallCullingOnly(self, onSegInspect = None):

        # optional function pointer when we inspect a visible seg
        self.onSegInspect = onSegInspect
        self.wallRenderer = self.renderRange

        # clear our clipping list of walls
        self.segList = [SolidSegmentRange(-100000, -1)]
        self.segList.append(SolidSegmentRange(self.width, 100000))
        self.clippings = {} # dict of segIds to screenXs

        # render 3d viewport
        self.map.renderBspNodes(self.player.x, self.player.y, self.renderSubsector)

    def renderWolfWalls(self, onSegInspect = None):

        # optional function pointer when we inspect a visible seg
        self.onSegInspect = onSegInspect
        self.wallRenderer = self.renderWolfWall

        # clear our clipping list of walls
        self.segList = [SolidSegmentRange(-100000, -1)]
        self.segList.append(SolidSegmentRange(self.width, 100000))
        self.clippings = {} # dict of segIds to screenXs

        # render 3d viewport
        self.map.renderBspNodes(self.player.x, self.player.y, self.renderSubsector)

    def renderSubsector(self, subsectorId):
        # iterate segs in subsector
        subsector = self.map.subsectors[subsectorId]
        for i in range(subsector.segCount):
            segId = subsector.firstSegID + i
            seg = self.map.segs[segId]
            linedef = self.map.linedefs[seg.linedefID]
            if linedef.isSolid() is False: # skip non-solid walls for now
                continue

            v1 = self.map.vertices[seg.startVertexID]
            v2 = self.map.vertices[seg.endVertexID]
            angles = self.clipVerticesToFov(v1, v2)

            if angles is not None:
                if self.onSegInspect is not None:
                    self.onSegInspect(seg, v1, v2)
                # get screen projection Xs
                v1xScreen = self.angleToScreen(angles[0])
                v2xScreen = self.angleToScreen(angles[1])

                # build wall clippings
                self.clipWall(segId, self.segList, v1xScreen, v2xScreen, self.clippings, angles, self.wallRenderer)

    def renderRange(self, segId, segPair, angles):
        # get unique color for this line
        linedef = self.map.linedefs[self.map.segs[segId].linedefID]
        sidedef = self.map.sidedefs[linedef.frontSideDef]
        rgba = self.getWallColor(sidedef.middleTexture)
        # hardcoded helper to render the range
        fpsStart = [segPair[0] + self.xOffset, self.yOffset]
        # ranges are exclusive of eachothers start and end
        # so add +1 to width (not for now because I like the line)
        width = segPair[1] - segPair[0] # + 1
        self.game.drawRectangle(fpsStart, width, self.height, rgba)

    def renderWolfWall(self, segId, segPair, angles):
        seg = self.map.segs[segId]
        self.calculateWallHeightWolfenstein(seg, segPair[0], segPair[1], angles[0], angles[1])

    def angleToScreen(self, angle):
        ix = 0
        halfWidth = (int)(self.width / 2)
        if angle.gtF(self.fov):
            # left side
            angle.isubF(self.fov)
            ix = halfWidth - (int)(math.tan(angle.toRadians()) * halfWidth)
        else:
            # right side
            angle = Angle(self.fov - angle.deg)
            ix = (int)(math.tan(angle.toRadians()) * halfWidth)
            ix += halfWidth
        return ix

    def clipSegToFov(self, seg):
        fov = Angle(self.fov)
        v1 = self.map.vertices[seg.startVertexID]
        v2 = self.map.vertices[seg.endVertexID]
        return self.clipVerticesToFov(v1, v2, fov)

    def clipVerticesToFov(self, v1, v2):
        fov = Angle(self.fov)
        v1Angle = self.player.angleToVertex(v1)
        v2Angle = self.player.angleToVertex(v2)
        spanAngle = v1Angle.subA(v2Angle)
        if spanAngle.gteF(self.fov * 2):
            return None
        # Cases
        #  ~: Seg left and right are in fov and fully visible
        #  A: Seg is all the way to the left and not visible
        #  B: Seg is to the right and not visible
        #  C: Right part of seg is visible and left is clipped
        #  D: Left part of seg is visible and right is clipped
        #  E: Left and right are clipped but middle is visible
        # segs must be facing us
        # segs are made of two vertices
        # rotate the seg minus the player angle
        v1Angle = v1Angle.subA(self.player.angle)
        v2Angle = v2Angle.subA(self.player.angle)
        # this puts their vertices around the 0 degree
        # left side of FOV is 45
        # right side of FOV = -45 (315)
        # if we rotate player to 45 then
        # left side is at 90
        # right side is at 0 (no negative comparisons)
        # if V1 is > 90 its outside
        # if V2 is < 0 its outside
        # v1 test:
        halfFov = fov.divF(2)
        v1Moved = v1Angle.addA(halfFov)
        if v1Moved.gtA(fov):
            # v1 is outside the fov
            # check if angle of v1 to v2 is also outside fov
            # by comparing how far v1 is away from fov
            # if more than dist v1 to v2 then the angle outside fov
            v1MovedAngle = v1Moved.subA(fov)
            if v1MovedAngle.gteA(spanAngle):
                return None

            # v2 is valid, clip v1
            v1Angle = halfFov
        # v2 test: (we cant have angle < 0 so subtract angle from halffov)
        v2Moved = halfFov.subA(v2Angle)
        if v2Moved.gtA(fov):
            v2Angle = halfFov.neg()

        # rerotate angles
        v1Angle.iaddA(fov)
        v2Angle.iaddA(fov)

        return v1Angle, v2Angle

    def getWallColor(self, textureId):
        if textureId in self.wallColors:
            return self.wallColors[textureId]
        rgba = (random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), 1)
        self.wallColors[textureId] = rgba
        return rgba

    # python DIY linked lists are a nightmare
    # because of the pass-object-by-reference
    # nature of variables
    # when I change next and prev values on a
    # node it changes it for that copy of the
    # variable, and not for the underlying reference
    # TODO take a seg and implement StoreWallRange
    # so that we can update the segs display range
    def clipWall(self, segId, segList, wallStart, wallEnd, clippings, angles, renderRange):
        segRange = None
        segIndex = None
        # skip all segments that end before this wall starts
        i=0
        while (i < len(segList) and segList[i].xEnd < wallStart - 1):
            i += 1
        segIndex = i
        segRange = segList[segIndex]
        # should always have a node since we cap our ends with
        # "infinity"
        # START to OVERLAP
        if wallStart < segRange.xStart:
            # found a position in the node list
            # are they overlapping?
            if wallEnd < segRange.xStart - 1:
                # all of the wall is visible to insert it
                # STOREWALL
                # StoreWallRange(seg, CurrentWall.XStart, CurrentWall.XEnd);
                clippings[segId] = (wallStart, wallEnd)
                renderRange(segId, clippings[segId], angles)
                segList.insert(segIndex, SolidSegmentRange(wallStart, wallEnd))
                # go to next wall
                return
            # if not overlapping, end is already included
            # so just update the start
            # STOREWALL
            # StoreWallRange(seg, CurrentWall.XStart, FoundClipWall->XStart - 1);
            clippings[segId] = (wallStart,  segRange.xStart - 1)
            renderRange(segId, clippings[segId], angles)
            segRange.xStart = wallStart
        # FULL OVERLAPPED
        # this part is already occupied
        if wallEnd <= segRange.xEnd:
            return # go to next wall

        # CHOP AND MERGE
        # start by looking at the next entry in the list
        # is the next entry within the current wall range?
        nextSegIndex = segIndex
        nextSegRange = segRange
        while wallEnd >= segList[nextSegIndex + 1].xStart - 1:
            # STOREWALL
            # StoreWallRange(seg, NextWall->XEnd + 1, next(NextWall, 1)->XStart - 1);
            clippings[segId] = (nextSegRange.xEnd + 1,  segList[nextSegIndex + 1].xStart - 1)
            renderRange(segId, clippings[segId], angles)
            nextSegIndex += 1
            nextSegRange = segList[nextSegIndex]
            # partially clipped by other walls, store each fragment
            if wallEnd <= nextSegRange.xEnd:
                segRange.xEnd = nextSegRange.xEnd
                if nextSegIndex != segIndex:
                    segIndex += 1
                    nextSegIndex += 1
                    del segList[segIndex:nextSegIndex]
                return

        # wall precedes all known segments
        # STOREWALL
        # StoreWallRange(seg, NextWall->XEnd + 1, CurrentWall.XEnd);
        clippings[segId] = (nextSegRange.xEnd + 1,  wallEnd)
        renderRange(segId, clippings[segId], angles)
        segRange.xEnd = wallEnd
        if (nextSegIndex != segIndex):
            segIndex += 1
            nextSegIndex += 1
            del segList[segIndex:nextSegIndex]
        return

    def printSegList(self, segList):
        for i,r in enumerate(segList):
            if i+1 < len(segList):
                print("{} > ".format(r), end='')
            else:
                print(r, end='')
        print('')

    def calculateCeilingFloorHeight(self, seg, vxScreen, distanceToV):
        # return ceilingVOnScreen, floorVOnScreen
        # seg front sector is the linedef's frontSideDef sector
        linedef = self.map.linedefs[seg.linedefID]
        frontSideDef = self.map.sidedefs[linedef.frontSideDef]
        frontSector = self.map.sectors[frontSideDef.sectorID]

        # get heights relative to eye position of player (camera)
        ceiling = frontSector.ceilingHeight - self.player.getEyeZ()
        floor = frontSector.floorHeight - self.player.getEyeZ()

        # get angle from precomputed lookup table
        vScreenAngle = self.screenXtoAngleLookup[vxScreen]

        # use angle to get projected screen position
        distanceToVScreen = self.distancePlayerToScreen / vScreenAngle.getCos()
        ceilingVOnScreen = (abs(ceiling) * distanceToVScreen) / distanceToV
        floorVOnScreen = (abs(floor) * distanceToVScreen) / distanceToV

        if ceiling > 0:
            ceilingVOnScreen = self.halfScreenHeight - ceilingVOnScreen
        else:
            ceilingVOnScreen += self.halfScreenHeight
        if floor > 0:
            floorVOnScreen = self.halfScreenHeight - floorVOnScreen
        else:
            floorVOnScreen += self.halfScreenHeight

        return ceilingVOnScreen, floorVOnScreen

    def calculateWallHeightWolfenstein(self, seg, v1xScreen, v2xScreen, v1Angle, v2Angle):
        v1 = self.map.vertices[seg.startVertexID]
        v2 = self.map.vertices[seg.endVertexID]

        # we have v1 and v2, do calculations for v1 and v2
        # separately then interpolate values in between
        distanceToV1 = self.player.distanceToVertex(v1)
        distanceToV2 = self.player.distanceToVertex(v2)

        # fix that clipped seg angles are weird
        # cant get this to not divide by zero so commenting out
        # it was temporary wolfenstein walls anyways
        # if v1xScreen <= 0:
        #     distanceToV1 = self.partialSegWolf(seg, v1, v2, v1Angle, v2Angle, distanceToV1, True)
        # if v2xScreen >= self.width - 1:
        #     distanceToV2 = self.partialSegWolf(seg, v1, v2, v1Angle, v2Angle, distanceToV2, False)

        # get projected positions on screen
        ceilingV1onScreen, floorV1onScreen = self.calculateCeilingFloorHeight(seg, v1xScreen, distanceToV1)
        ceilingV2onScreen, floorV2onScreen = self.calculateCeilingFloorHeight(seg, v2xScreen, distanceToV2)

        # get wall color
        linedef = self.map.linedefs[seg.linedefID]
        frontSidedef = self.map.sidedefs[linedef.frontSideDef]
        rgba = self.getWallColor(frontSidedef.middleTexture)

        # draw polygon of wall
        # left side
        lx = v1xScreen + self.xOffset
        rx = v2xScreen + self.xOffset
        lcy = ceilingV1onScreen + self.yOffset
        rcy = ceilingV2onScreen + self.yOffset
        lfy = floorV1onScreen + self.yOffset
        rfy = floorV2onScreen + self.yOffset
        self.game.drawLine([lx, lcy], [lx, lfy], rgba, 1)
        # right side
        self.game.drawLine([rx, rcy], [rx, rfy], rgba, 1)
        # top
        self.game.drawLine([lx, lcy], [rx, rcy], rgba, 1)
        # bottom
        self.game.drawLine([lx, lfy], [rx, rfy], rgba, 1)

    def partialSegWolf(self, seg, v1, v2, v1Angle, v2Angle, distanceToV, isLeftSide):
        # dunno wtf is going on here
        # and I cant get it to work because it divides by zero
        sideC = math.sqrt((v1.x - v2.x) ** 2 + (v1.y - v2.y) ** 2)
        v1v2Span = Angle(v1Angle.deg - v2Angle.deg)
        sineAngleB = distanceToV * v1v2Span.getSin() / sideC
        angleB = Angle(math.asin(sineAngleB) * 180 / math.pi)
        angleA = Angle(180 - v1v2Span.deg - angleB.deg)

        angleVtoFov = None
        if isLeftSide:
            angleVtoFov = Angle(v1Angle.deg - (self.player.angle.deg + self.fov/2))
        else:
            angleVtoFov = Angle((self.player.angle.deg - self.fov/2) - v2Angle.deg)

        newAngleB = Angle(180 - angleVtoFov.deg - angleA.deg)
        distanceToV = distanceToV * angleA.getSin() / newAngleB.getSin() # divde by 0 error

        return distanceToV


