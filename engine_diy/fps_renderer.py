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

        self.halfScreenWidth = width / 2
        self.halfScreenHeight = height / 2
        self.halfFov = Angle(fov / 2)
        self.distancePlayerToScreen = self.halfScreenWidth / self.halfFov.getTan() # 160 at 320 width and 90 fov

        # build lookup table of all x screen coords and
        # their projection angles
        # this was part of the wolfenstein height projection
        self.wolfenstein_screenXToAngleLookup = []
        screenAngle = Angle(fov / 2)
        step = fov / (width + 1) # why +1?
        for i in range(0, width + 1):
            self.wolfenstein_screenXToAngleLookup.append(screenAngle)
            screenAngle = screenAngle.subF(step)

        self.doomclassic_screenXToAngleLookup = []
        screenAngle = Angle(fov / 2)
        step = fov / (width + 1) # why +1?
        for i in range(0, width + 1):
            self.doomclassic_screenXToAngleLookup.append(screenAngle)
            screenAngle = screenAngle.subF(step)

    def printSegList(self, segList):
        for i,r in enumerate(segList):
            if i+1 < len(segList):
                print("{} > ".format(r), end='')
            else:
                print(r, end='')
        print('')

    def getWallColor(self, textureId):
        if textureId in self.wallColors:
            return self.wallColors[textureId]
        rgba = (random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), 1)
        self.wallColors[textureId] = rgba
        return rgba



    ###############################
    ## EDGES ONLY RENDER METHODS ##
    ###############################

    def edges_render(self, solidOnly = False, onSegInspect = None):
        # loop over all segs
        for i, seg in enumerate(self.map.segs):
            linedef = self.map.linedefs[seg.linedefID]
            # if in mode 8 only render solid walls
            if solidOnly and linedef.isSolid() is False:
                continue

            v1 = self.map.vertices[seg.startVertexID]
            v2 = self.map.vertices[seg.endVertexID]
            angles = self.edges_clipVerticesToFov(v1, v2)

            if angles is not None:
                if onSegInspect is not None:
                    onSegInspect(seg, v1, v2)

                # render fps window for all walls
                v1xScreen = self.edges_angleToScreen(angles[0])
                v2xScreen = self.edges_angleToScreen(angles[1])

                # wall edge1
                fpsStart = [v1xScreen + self.xOffset, self.yOffset]
                fpsEnd = [v1xScreen + self.xOffset, self.height + self.yOffset]
                self.game.drawLine(fpsStart, fpsEnd, (1,1,0,1), 1)

                # wall edge 2
                fpsStart = [v2xScreen + self.xOffset, self.yOffset]
                fpsEnd = [v2xScreen + self.xOffset, self.height + self.yOffset]
                self.game.drawLine(fpsStart, fpsEnd, (1,0,1,1), 1)

    def edges_clipVerticesToFov(self, v1, v2):
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

    def edges_angleToScreen(self, angle):
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





    ##############################
    ## WALL CULL RENDER METHODS ##
    ##############################

    def wallcull_render(self, onSegInspect = None):

        # optional function pointer when we inspect a visible seg
        self.onSegInspect = onSegInspect
        self.wallRenderer = self.wallcull_renderRange

        # clear our clipping list of walls
        self.segList = [SolidSegmentRange(-100000, -1)]
        self.segList.append(SolidSegmentRange(self.width, 100000))
        self.clippings = {} # dict of segIds to screenXs

        # render 3d viewport
        self.map.renderBspNodes(self.player.x, self.player.y, self.wallcull_renderSubsector)

    def wallcull_renderRange(self, segId, segPair, angles):
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

    def wallcull_renderSubsector(self, subsectorId):
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
            angles = self.wallcull_clipVerticesToFov(v1, v2)

            if angles is not None:
                if self.onSegInspect is not None:
                    self.onSegInspect(seg, v1, v2)

                # get screen projection Xs
                v1xScreen = self.wallcull_angleToScreen(angles[0])
                v2xScreen = self.wallcull_angleToScreen(angles[1])

                # build wall clippings
                self.wallcull_clipWall(segId, self.segList, v1xScreen, v2xScreen, self.clippings, angles, self.wallRenderer)

    def wallcull_angleToScreen(self, angle):
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

    def wallcull_clipVerticesToFov(self, v1, v2):
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

    # python DIY linked lists are a nightmare
    # because of the pass-object-by-reference
    # nature of variables
    # when I change next and prev values on a
    # node it changes it for that copy of the
    # variable, and not for the underlying reference
    # TODO take a seg and implement StoreWallRange
    # so that we can update the segs display range
    def wallcull_clipWall(self, segId, segList, wallStart, wallEnd, clippings, angles, rangeRenderer):
        if len(segList) < 2:
            return
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
                rangeRenderer(segId, clippings[segId], angles)
                segList.insert(segIndex, SolidSegmentRange(wallStart, wallEnd))
                # go to next wall
                return
            # if not overlapping, end is already included
            # so just update the start
            # STOREWALL
            # StoreWallRange(seg, CurrentWall.XStart, FoundClipWall->XStart - 1);
            clippings[segId] = (wallStart,  segRange.xStart - 1)
            rangeRenderer(segId, clippings[segId], angles)
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
            rangeRenderer(segId, clippings[segId], angles)

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
        rangeRenderer(segId, clippings[segId], angles)
        segRange.xEnd = wallEnd

        if (nextSegIndex != segIndex):
            segIndex += 1
            nextSegIndex += 1
            del segList[segIndex:nextSegIndex]
        return







    ################################
    ## WOLFENSTEIN RENDER METHODS ##
    ################################

    def wolfenstein_render(self, onSegInspect = None):

        # optional function pointer when we inspect a visible seg
        self.onSegInspect = onSegInspect
        self.wallRenderer = self.wolfenstein_renderWall

        # clear our clipping list of walls
        self.segList = [SolidSegmentRange(-100000, -1)]
        self.segList.append(SolidSegmentRange(self.width, 100000))
        self.clippings = {} # dict of segIds to screenXs

        # render 3d viewport
        self.map.renderBspNodes(self.player.x, self.player.y, self.wolfenstein_renderSubsector)

    def wolfenstein_renderSubsector(self, subsectorId):
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
            angles = self.wolfenstein_clipVerticesToFov(v1, v2)

            if angles is not None:
                if self.onSegInspect is not None:
                    self.onSegInspect(seg, v1, v2)

                # get screen projection Xs
                v1xScreen = self.wolfenstein_angleToScreen(angles[0])
                v2xScreen = self.wolfenstein_angleToScreen(angles[1])

                # build wall clippings
                self.wolfenstein_clipWall(segId, self.segList, v1xScreen, v2xScreen, self.clippings, angles, self.wallRenderer)

    def wolfenstein_angleToScreen(self, angle):
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

    def wolfenstein_clipVerticesToFov(self, v1, v2):
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

    def wolfenstein_renderWall(self, segId, segPair, angles):
        seg = self.map.segs[segId]
        self.wolfenstein_calculateWallHeight(seg, segPair[0], segPair[1], angles[0], angles[1])

    def wolfenstein_calculateWallHeight(self, seg, v1xScreen, v2xScreen, v1Angle, v2Angle):
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
        #     distanceToV1 = self.wolfenstein_partialSeg(seg, v1, v2, v1Angle, v2Angle, distanceToV1, True)
        # if v2xScreen >= self.width - 1:
        #     distanceToV2 = self.wolfenstein_partialSeg(seg, v1, v2, v1Angle, v2Angle, distanceToV2, False)

        # get projected positions on screen
        ceilingV1onScreen, floorV1onScreen = self.wolfenstein_calculateCeilingFloorHeight(seg, v1xScreen, distanceToV1)
        ceilingV2onScreen, floorV2onScreen = self.wolfenstein_calculateCeilingFloorHeight(seg, v2xScreen, distanceToV2)

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

    def wolfenstein_calculateCeilingFloorHeight(self, seg, vxScreen, distanceToV):
        # return ceilingVOnScreen, floorVOnScreen
        # seg front sector is the linedef's frontSideDef sector
        linedef = self.map.linedefs[seg.linedefID]
        frontSideDef = self.map.sidedefs[linedef.frontSideDef]
        frontSector = self.map.sectors[frontSideDef.sectorID]

        # get heights relative to eye position of player (camera)
        ceiling = frontSector.ceilingHeight - self.player.getEyeZ()
        floor = frontSector.floorHeight - self.player.getEyeZ()

        # get angle from precomputed lookup table
        vScreenAngle = self.wolfenstein_screenXToAngleLookup[vxScreen]

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

    def wolfenstein_partialSeg(self, seg, v1, v2, v1Angle, v2Angle, distanceToV, isLeftSide):
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

    # python DIY linked lists are a nightmare
    # because of the pass-object-by-reference
    # nature of variables
    # when I change next and prev values on a
    # node it changes it for that copy of the
    # variable, and not for the underlying reference
    # TODO take a seg and implement StoreWallRange
    # so that we can update the segs display range
    def wolfenstein_clipWall(self, segId, segList, wallStart, wallEnd, clippings, angles, rangeRenderer):
        if len(segList) < 2:
            return
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
                rangeRenderer(segId, clippings[segId], angles)
                segList.insert(segIndex, SolidSegmentRange(wallStart, wallEnd))
                # go to next wall
                return
            # if not overlapping, end is already included
            # so just update the start
            # STOREWALL
            # StoreWallRange(seg, CurrentWall.XStart, FoundClipWall->XStart - 1);
            clippings[segId] = (wallStart,  segRange.xStart - 1)
            rangeRenderer(segId, clippings[segId], angles)
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
            rangeRenderer(segId, clippings[segId], angles)

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
        rangeRenderer(segId, clippings[segId], angles)
        segRange.xEnd = wallEnd

        if (nextSegIndex != segIndex):
            segIndex += 1
            nextSegIndex += 1
            del segList[segIndex:nextSegIndex]
        return







    #################################
    ## DOOM CLASSIC RENDER METHODS ##
    #################################

    def doomclassic_render(self, onSegInspect = None):
        # optional function pointer when we inspect a visible seg
        self.onSegInspect = onSegInspect
        self.wallRenderer = self.doomclassic_renderWall

        # clear our clipping list of walls
        self.segList = [SolidSegmentRange(-100000, -1)]
        self.segList.append(SolidSegmentRange(self.width, 100000))
        self.clippings = {} # dict of segIds to screenXs

        # render 3d viewport
        self.map.renderBspNodes(self.player.x, self.player.y, self.doomclassic_renderSubsector)

    def doomclassic_renderSubsector(self, subsectorId):
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
            angles = self.doomclassic_clipVerticesToFov(v1, v2)

            if angles is not None:
                if self.onSegInspect is not None:
                    self.onSegInspect(seg, v1, v2)

                # get screen projection Xs
                v1xScreen = self.doomclassic_angleToScreen(angles[0])
                v2xScreen = self.doomclassic_angleToScreen(angles[1])

                # build wall clippings
                self.doomclassic_clipWall(segId, self.segList, v1xScreen, v2xScreen, self.clippings, angles, self.wallRenderer)

    def doomclassic_renderWall(self, segId, segPair, angles):
        seg = self.map.segs[segId]
        self.doomclassic_calculateWallHeight(seg, segPair[0], segPair[1], angles[0], angles[1])

    def doomclassic_calculateWallHeight(self, seg, v1xScreen, v2xScreen, v1Angle, v2Angle):
        # get seg data
        v1 = self.map.vertices[seg.startVertexID]
        v2 = self.map.vertices[seg.endVertexID]
        linedef = self.map.linedefs[seg.linedefID]
        frontSidedef = self.map.sidedefs[linedef.frontSideDef]
        frontSector = self.map.sectors[frontSidedef.sectorID]
        rgba = self.getWallColor(frontSidedef.middleTexture)

        # calculate distance to first edge of the wall
        angle90 = Angle(90)
        segToNormalAngle = Angle(seg.angle + angle90.deg)
        normalToV1Angle = segToNormalAngle.subA(v1Angle)

        # normal angle is 90deg to wall
        segToPlayerAngle = angle90.subA(normalToV1Angle)

        distanceToV1 = self.player.distanceToVertex(v1)
        distanceToNormal = segToPlayerAngle.getSin() * distanceToV1

        debug = v1.x == 832
        v1ScaleFactor = self.doomclassic_getScaleFactor(v1xScreen, segToNormalAngle, distanceToNormal, debug)
        v2ScaleFactor = self.doomclassic_getScaleFactor(v2xScreen, segToNormalAngle, distanceToNormal, debug)

        # TODO I added this because of divide by zero
        # I think my wall clipping is adding walls with
        # the same xscreen for both ends
        # this would be walls that are exactly ahead of us
        # and I think they should be culled
        if v2xScreen == v1xScreen:
            steps = 1
        else:
            steps = (v2ScaleFactor - v1ScaleFactor) / (v2xScreen - v1xScreen)

        if debug:
            print(v1xScreen, v2xScreen, v1, v2)
            print(v1xScreen, v2xScreen, v1ScaleFactor, v2ScaleFactor, steps, flush=True)

        # get heights relative to eye position of player (camera)
        ceiling = frontSector.ceilingHeight - self.player.getEyeZ()
        floor = frontSector.floorHeight - self.player.getEyeZ()

        ceilingStep = -(ceiling * steps)
        ceilingEnd = self.halfScreenHeight - (ceiling * v1ScaleFactor)

        floorStep = -(floor * steps)
        floorStart = self.halfScreenHeight - (floor * v1ScaleFactor)

        iXCurrent = v1xScreen
        while iXCurrent <= v2xScreen:
            drawStart = [iXCurrent + self.xOffset, ceilingEnd + self.yOffset]
            drawEnd = [iXCurrent + self.xOffset, floorStart + self.yOffset]
            if iXCurrent % 2 == 0:
                self.game.drawLine(drawStart, drawEnd, rgba, 1)
            iXCurrent += 1
            ceilingEnd += ceilingStep
            floorStart += floorStep

    # Method in DOOM engine that calculated a wall height
    # scale factor given a distance of the wall from the screen
    # and the distance of that same angle from the player to screen
    def doomclassic_getScaleFactor(self, vxScreen, segToNormalAngle, distanceToNormal, debug=False):
        # constants used with some issues for DOOM textures
        MAX_SCALEFACTOR = 64.0
        MIN_SCALEFACTOR = 0.00390625

        angle90 = Angle(90)
        screenXAngle = self.doomclassic_screenXToAngleLookup[vxScreen] # Angle object
        skewAngle = screenXAngle.addA(self.player.angle).subA(segToNormalAngle)
        #skewAngle = Angle(screenXAngle.deg + self.player.angle.deg - segToNormalAngle.deg)

        if debug:
            print(vxScreen, screenXAngle, skewAngle)

        # get scale factor
        screenXAngleCos = screenXAngle.getCos()
        skewAngleCos = skewAngle.getCos()
        scaleFactor = (self.distancePlayerToScreen * skewAngleCos) / (distanceToNormal * screenXAngleCos)

        # clamp
        scaleFactor = min(MAX_SCALEFACTOR, max(MIN_SCALEFACTOR, scaleFactor))
        return scaleFactor

    def doomclassic_angleToScreen(self, angle):
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

    def doomclassic_clipVerticesToFov(self, v1, v2):
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

    # python DIY linked lists are a nightmare
    # because of the pass-object-by-reference
    # nature of variables
    # when I change next and prev values on a
    # node it changes it for that copy of the
    # variable, and not for the underlying reference
    # TODO take a seg and implement StoreWallRange
    # so that we can update the segs display range
    def doomclassic_clipWall(self, segId, segList, wallStart, wallEnd, clippings, angles, rangeRenderer):
        if len(segList) < 2:
            return
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
                rangeRenderer(segId, clippings[segId], angles)
                segList.insert(segIndex, SolidSegmentRange(wallStart, wallEnd))
                # go to next wall
                return
            # if not overlapping, end is already included
            # so just update the start
            # STOREWALL
            # StoreWallRange(seg, CurrentWall.XStart, FoundClipWall->XStart - 1);
            clippings[segId] = (wallStart,  segRange.xStart - 1)
            rangeRenderer(segId, clippings[segId], angles)
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
            rangeRenderer(segId, clippings[segId], angles)

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
        rangeRenderer(segId, clippings[segId], angles)
        segRange.xEnd = wallEnd

        if (nextSegIndex != segIndex):
            segIndex += 1
            nextSegIndex += 1
            del segList[segIndex:nextSegIndex]
        return


