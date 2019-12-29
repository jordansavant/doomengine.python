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

        self.f_fov = fov
        self.f_width = width
        self.f_height = height
        self.f_xOffset = xOffset
        self.f_yOffset = yOffset

        self.wallColors = {} # helper to map a texture to a single color (until textures are added)
        self.onSegInspect = None # function pointer for helping to visualize segs in fps viewport

        self.f_halfWidth = width / 2
        self.f_halfHeight = height / 2
        self.a_halfFov = Angle(fov / 2)
        self.f_distancePlayerToScreen = self.f_halfWidth / self.a_halfFov.getTan() # 160 at 320 width and 90 fov

        # build lookup table of all x screen coords and
        # their projection angles
        # this was part of the wolfenstein height projection
        self.wolfenstein_screenXToAngleLookup = []
        screenAngle = Angle(fov / 2)
        step = fov / (width + 1) # why +1?
        for i in range(0, width + 1):
            self.wolfenstein_screenXToAngleLookup.append(screenAngle.new())
            screenAngle = screenAngle.subF(step)

        self.doomsolids_screenXToAngleLookup = []
        for i in range(0, width + 1):
            f_angle = math.atan((self.f_halfWidth - i) / float(self.f_distancePlayerToScreen)) * 180 / math.pi
            self.doomsolids_screenXToAngleLookup.append(Angle(f_angle))

        self.doomportals_screenXToAngleLookup = []
        for i in range(0, width + 1):
            f_angle = math.atan((self.f_halfWidth - i) / float(self.f_distancePlayerToScreen)) * 180 / math.pi
            self.doomportals_screenXToAngleLookup.append(Angle(f_angle))
        self.doomportals_ceilingClipHeight = []
        self.doomportals_floorClipHeight = []
        for i in range(0, self.f_width):
            self.doomportals_ceilingClipHeight.append(-1)
            self.doomportals_floorClipHeight.append(int(self.f_height))

        self.doomhistory_screenXToAngleLookup = []
        for i in range(0, width + 1):
            f_angle = math.atan((self.f_halfWidth - i) / float(self.f_distancePlayerToScreen)) * 180 / math.pi
            self.doomhistory_screenXToAngleLookup.append(Angle(f_angle))
        self.doomhistory_ceilingClipHeight = []
        self.doomhistory_floorClipHeight = []
        for i in range(0, self.f_width):
            self.doomhistory_ceilingClipHeight.append(-1)
            self.doomhistory_floorClipHeight.append(int(self.f_height))
        self.doomhistory_frameSegsDrawData = []

        self.debug = False

    def printSegList(self, segList):
        for i,r in enumerate(segList):
            if i+1 < len(segList):
                print("{} > ".format(r), end='')
            else:
                print(r, end='')
        print('')

    def getWallColor(self, textureId, lightLevel = None):
        if textureId in self.wallColors:
            rgba = self.wallColors[textureId]
        else:
            rgba = (random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), 1)
            self.wallColors[textureId] = rgba
        # adjust for light level
        if lightLevel is not None: # 0 - 255
            fl = float(lightLevel) / 255.0
            rgba = (rgba[0] * fl, rgba[1] * fl, rgba[2] * fl, rgba[3])
        return rgba



    ###############################
    ## EDGES ONLY RENDER METHODS ##
    ###############################

    def edges_render(self, solidOnly = False, onSegInspect = None):
        # loop over all segs
        for i, seg in enumerate(self.map.segs):
            linedef = seg.linedef
            # if in mode 8 only render solid walls
            if solidOnly and linedef.isSolid() is False:
                continue

            v1 = seg.startVertex
            v2 = seg.endVertex
            angles = self.edges_clipVerticesToFov(v1, v2)

            if angles is not None:
                if onSegInspect is not None:
                    onSegInspect(seg, v1, v2)

                # render fps window for all walls
                v1xScreen = self.edges_angleToScreen(angles[0])
                v2xScreen = self.edges_angleToScreen(angles[1])

                # wall edge1
                fpsStart = [v1xScreen + self.f_xOffset, self.f_yOffset]
                fpsEnd = [v1xScreen + self.f_xOffset, self.f_height + self.f_yOffset]
                self.game.drawLine(fpsStart, fpsEnd, (1,1,0,1), 1)

                # wall edge 2
                fpsStart = [v2xScreen + self.f_xOffset, self.f_yOffset]
                fpsEnd = [v2xScreen + self.f_xOffset, self.f_height + self.f_yOffset]
                self.game.drawLine(fpsStart, fpsEnd, (1,0,1,1), 1)

    def edges_clipVerticesToFov(self, v1, v2):
        fov = Angle(self.f_fov)
        v1Angle = self.player.angleToVertex(v1)
        v2Angle = self.player.angleToVertex(v2)
        spanAngle = v1Angle.subA(v2Angle)
        if spanAngle.gteF(self.f_fov * 2):
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
        halfWidth = (int)(self.f_width / 2)
        if angle.gtF(self.f_fov):
            # left side
            angle.isubF(self.f_fov)
            ix = halfWidth - (int)(math.tan(angle.toRadians()) * halfWidth)
        else:
            # right side
            angle = Angle(self.f_fov - angle.deg)
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
        self.segList.append(SolidSegmentRange(self.f_width, 100000))
        self.clippings = {} # dict of segIds to screenXs

        # render 3d viewport
        self.map.renderBspNodes(self.player.x, self.player.y, self.wallcull_renderSubsector)

    def wallcull_renderRange(self, seg, segPair, angles):
        # get unique color for this line
        sidedef = seg.linedef.frontSidedef
        rgba = self.getWallColor(sidedef.middleTexture)

        # hardcoded helper to render the range
        fpsStart = [segPair[0] + self.f_xOffset, self.f_yOffset]

        # ranges are exclusive of eachothers start and end
        # so add +1 to width (not for now because I like the line)
        width = segPair[1] - segPair[0] # + 1
        self.game.drawRectangle(fpsStart, width, self.f_height, rgba)

    def wallcull_renderSubsector(self, subsector):
        # iterate segs in subsector
        for i in range(subsector.segCount):
            segId = subsector.firstSegID + i
            seg = self.map.segs[segId]
            linedef = seg.linedef
            if linedef.isSolid() is False: # skip non-solid walls for now
                continue

            v1 = seg.startVertex
            v2 = seg.endVertex
            angles = self.wallcull_clipVerticesToFov(v1, v2)

            if angles is not None:
                if self.onSegInspect is not None:
                    self.onSegInspect(seg, v1, v2)

                # get screen projection Xs
                v1xScreen = self.wallcull_angleToScreen(angles[0])
                v2xScreen = self.wallcull_angleToScreen(angles[1])

                # build wall clippings
                self.wallcull_clipWall(seg, self.segList, v1xScreen, v2xScreen, self.clippings, angles, self.wallRenderer)

    def wallcull_angleToScreen(self, angle):
        ix = 0
        halfWidth = (int)(self.f_width / 2)
        if angle.gtF(self.f_fov):
            # left side
            angle.isubF(self.f_fov)
            ix = halfWidth - (int)(math.tan(angle.toRadians()) * halfWidth)
        else:
            # right side
            angle = Angle(self.f_fov - angle.deg)
            ix = (int)(math.tan(angle.toRadians()) * halfWidth)
            ix += halfWidth
        return ix

    def wallcull_clipVerticesToFov(self, v1, v2):
        fov = Angle(self.f_fov)
        v1Angle = self.player.angleToVertex(v1)
        v2Angle = self.player.angleToVertex(v2)
        spanAngle = v1Angle.subA(v2Angle)
        if spanAngle.gteF(self.f_fov * 2):
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
    def wallcull_clipWall(self, seg, segList, wallStart, wallEnd, clippings, angles, rangeRenderer):
        if len(segList) < 2:
            return
        segId = seg.ID
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
                rangeRenderer(seg, clippings[segId], angles)
                segList.insert(segIndex, SolidSegmentRange(wallStart, wallEnd))
                # go to next wall
                return
            # if not overlapping, end is already included
            # so just update the start
            # STOREWALL
            # StoreWallRange(seg, CurrentWall.XStart, FoundClipWall->XStart - 1);
            clippings[segId] = (wallStart,  segRange.xStart - 1)
            rangeRenderer(seg, clippings[segId], angles)
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
            rangeRenderer(seg, clippings[segId], angles)

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
        rangeRenderer(seg, clippings[segId], angles)
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
        self.segList.append(SolidSegmentRange(self.f_width, 100000))
        self.clippings = {} # dict of segIds to screenXs

        # render 3d viewport
        self.map.renderBspNodes(self.player.x, self.player.y, self.wolfenstein_renderSubsector)

    def wolfenstein_renderSubsector(self, subsector):
        # iterate segs in subsector
        for i in range(subsector.segCount):
            segId = subsector.firstSegID + i
            seg = self.map.segs[segId]
            linedef = seg.linedef
            if linedef.isSolid() is False: # skip non-solid walls for now
                continue

            v1 = seg.startVertex
            v2 = seg.endVertex
            angles = self.wolfenstein_clipVerticesToFov(v1, v2)

            if angles is not None:
                if self.onSegInspect is not None:
                    self.onSegInspect(seg, v1, v2)

                # get screen projection Xs
                v1xScreen = self.wolfenstein_angleToScreen(angles[0])
                v2xScreen = self.wolfenstein_angleToScreen(angles[1])

                # build wall clippings
                self.wolfenstein_clipWall(seg, self.segList, v1xScreen, v2xScreen, self.clippings, angles, self.wallRenderer)

    def wolfenstein_angleToScreen(self, angle):
        ix = 0
        halfWidth = (int)(self.f_width / 2)
        if angle.gtF(self.f_fov):
            # left side
            angle.isubF(self.f_fov)
            ix = halfWidth - (int)(math.tan(angle.toRadians()) * halfWidth)
        else:
            # right side
            angle = Angle(self.f_fov - angle.deg)
            ix = (int)(math.tan(angle.toRadians()) * halfWidth)
            ix += halfWidth
        return ix

    def wolfenstein_clipVerticesToFov(self, v1, v2):
        fov = Angle(self.f_fov)
        v1Angle = self.player.angleToVertex(v1)
        v2Angle = self.player.angleToVertex(v2)
        spanAngle = v1Angle.subA(v2Angle)
        if spanAngle.gteF(self.f_fov * 2):
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

    def wolfenstein_renderWall(self, seg, segPair, angles):
        self.wolfenstein_calculateWallHeight(seg, segPair[0], segPair[1], angles[0], angles[1])

    def wolfenstein_calculateWallHeight(self, seg, v1xScreen, v2xScreen, v1Angle, v2Angle):
        v1 = seg.startVertex
        v2 = seg.endVertex

        # we have v1 and v2, do calculations for v1 and v2
        # separately then interpolate values in between
        distanceToV1 = self.player.distanceToVertex(v1)
        distanceToV2 = self.player.distanceToVertex(v2)

        # fix that clipped seg angles are weird
        # cant get this to not divide by zero so commenting out
        # it was temporary wolfenstein walls anyways
        # if v1xScreen <= 0:
        #     distanceToV1 = self.wolfenstein_partialSeg(seg, v1, v2, v1Angle, v2Angle, distanceToV1, True)
        # if v2xScreen >= self.f_width - 1:
        #     distanceToV2 = self.wolfenstein_partialSeg(seg, v1, v2, v1Angle, v2Angle, distanceToV2, False)

        # get projected positions on screen
        ceilingV1onScreen, floorV1onScreen = self.wolfenstein_calculateCeilingFloorHeight(seg, v1xScreen, distanceToV1)
        ceilingV2onScreen, floorV2onScreen = self.wolfenstein_calculateCeilingFloorHeight(seg, v2xScreen, distanceToV2)

        # get wall color
        frontSidedef = seg.linedef.frontSidedef
        rgba = self.getWallColor(frontSidedef.middleTexture)

        # draw polygon of wall
        # left side
        lx = v1xScreen + self.f_xOffset
        rx = v2xScreen + self.f_xOffset
        lcy = ceilingV1onScreen + self.f_yOffset
        rcy = ceilingV2onScreen + self.f_yOffset
        lfy = floorV1onScreen + self.f_yOffset
        rfy = floorV2onScreen + self.f_yOffset
        self.game.drawLine([lx, lcy], [lx, lfy], rgba, 1)
        # right side
        self.game.drawLine([rx, rcy], [rx, rfy], rgba, 1)
        # top
        self.game.drawLine([lx, lcy], [rx, rcy], rgba, 1)
        # bottom
        self.game.drawLine([lx, lfy], [rx, rfy], rgba, 1)

    def wolfenstein_calculateCeilingFloorHeight(self, seg, vxScreen, distanceToV):
        # return ceilingVOnScreen, floorVOnScreen
        # seg front sector is the linedef's frontSidedefID sector
        frontSector = seg.linedef.frontSidedef.sector

        # get heights relative to eye position of player (camera)
        ceiling = frontSector.ceilingHeight - self.player.getEyeZ()
        floor = frontSector.floorHeight - self.player.getEyeZ()

        # get angle from precomputed lookup table
        vScreenAngle = self.wolfenstein_screenXToAngleLookup[vxScreen]

        # use angle to get projected screen position
        distanceToVScreen = self.f_distancePlayerToScreen / vScreenAngle.getCos()
        ceilingVOnScreen = (abs(ceiling) * distanceToVScreen) / distanceToV
        floorVOnScreen = (abs(floor) * distanceToVScreen) / distanceToV

        if ceiling > 0:
            ceilingVOnScreen = self.f_halfHeight - ceilingVOnScreen
        else:
            ceilingVOnScreen += self.f_halfHeight
        if floor > 0:
            floorVOnScreen = self.f_halfHeight - floorVOnScreen
        else:
            floorVOnScreen += self.f_halfHeight

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
            angleVtoFov = Angle(v1Angle.deg - (self.player.angle.deg + self.f_fov/2))
        else:
            angleVtoFov = Angle((self.player.angle.deg - self.f_fov/2) - v2Angle.deg)

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
    def wolfenstein_clipWall(self, seg, segList, wallStart, wallEnd, clippings, angles, rangeRenderer):
        if len(segList) < 2:
            return
        segId = seg.ID
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
                rangeRenderer(seg, clippings[segId], angles)
                segList.insert(segIndex, SolidSegmentRange(wallStart, wallEnd))
                # go to next wall
                return
            # if not overlapping, end is already included
            # so just update the start
            # STOREWALL
            # StoreWallRange(seg, CurrentWall.XStart, FoundClipWall->XStart - 1);
            clippings[segId] = (wallStart,  segRange.xStart - 1)
            rangeRenderer(seg, clippings[segId], angles)
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
            rangeRenderer(seg, clippings[segId], angles)

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
        rangeRenderer(seg, clippings[segId], angles)
        segRange.xEnd = wallEnd

        if (nextSegIndex != segIndex):
            segIndex += 1
            nextSegIndex += 1
            del segList[segIndex:nextSegIndex]
        return







    ################################
    ## DOOM SOLIDS RENDER METHODS ##
    ################################

    def doomsolids_render(self, onSegInspect = None):
        # optional function pointer when we inspect a visible seg
        self.onSegInspect = onSegInspect
        self.wallRenderer = self.doomsolids_renderWall

        # clear our clipping list of walls
        self.segList = [SolidSegmentRange(-100000, -1)]
        self.segList.append(SolidSegmentRange(self.f_width, 100000))
        self.clippings = {} # dict of segIds to screenXs

        # render 3d viewport
        self.map.renderBspNodes(self.player.x, self.player.y, self.doomsolids_renderSubsector)

    def doomsolids_renderSubsector(self, subsector):
        # iterate segs in subsector
        for i in range(subsector.segCount):
            segId = subsector.firstSegID + i
            seg = self.map.segs[segId]
            linedef = seg.linedef
            if linedef.isSolid() is False: # skip non-solid walls for now
                continue

            v1 = seg.startVertex
            v2 = seg.endVertex
            # four angles
            angles = self.doomsolids_clipVerticesToFov(v1, v2)

            if angles is not None:
                if self.onSegInspect is not None:
                    self.onSegInspect(seg, v1, v2)

                v1Angle = angles[0]
                v2Angle = angles[1]
                v1AngleFromPlayer = angles[2]
                v2AngleFromPlayer = angles[3]

                self.doomsolids_addWallInFov(seg, v1Angle, v2Angle, v1AngleFromPlayer, v2AngleFromPlayer)

    def doomsolids_addWallInFov(self, seg, v1Angle, v2Angle, v1AngleFromPlayer, v2AngleFromPlayer):
        v1 = seg.startVertex
        v2 = seg.endVertex

        # get screen projection Xs
        v1xScreen = self.doomsolids_angleToScreen(v1AngleFromPlayer)
        v2xScreen = self.doomsolids_angleToScreen(v2AngleFromPlayer)

        # skip same pixel wall
        if v1xScreen == v2xScreen:
            return

        # skip nonsolid walls
        if seg.linedef.isSolid() is False:
            return

        # build wall clippings
        self.doomsolids_clipWall(seg, self.segList, v1xScreen, v2xScreen, v1Angle, v2Angle, self.clippings, self.wallRenderer)

    def doomsolids_renderWall(self, seg, segPair, v1Angle, v2Angle):
        self.doomsolids_calculateWallHeight(seg, segPair[0], segPair[1], v1Angle, v2Angle)

    def doomsolids_calculateWallHeight(self, seg, v1xScreen, v2xScreen, v1Angle, v2Angle):
        # get seg data
        v1 = seg.startVertex
        v2 = seg.endVertex

        # get texture color
        frontSidedef = seg.linedef.frontSidedef
        frontSector = frontSidedef.sector
        rgba = self.getWallColor(frontSidedef.middleTexture, frontSector.lightLevel)

        # calculate distance to first edge of the wall
        angle90 = Angle(90)
        segToNormalAngle = Angle(seg.getAngle() + angle90.deg)
        normalToV1Angle = segToNormalAngle.subA(v1Angle)

        # normal angle is 90deg to wall
        segToPlayerAngle = angle90.subA(normalToV1Angle)

        f_distanceToV1 = self.player.distanceToVertex(v1)
        f_distanceToNormal = segToPlayerAngle.getSin() * f_distanceToV1

        v1ScaleFactor = self.doomsolids_getScaleFactor(v1xScreen, segToNormalAngle, f_distanceToNormal)
        v2ScaleFactor = self.doomsolids_getScaleFactor(v2xScreen, segToNormalAngle, f_distanceToNormal)

        # screen xs can be the same so avoid div/0
        # if they are the same that means they occupy
        # one pixel
        # DIY tutorial (c++) does divide by zero
        # and when
        if v1xScreen == v2xScreen:
            steps = 1
        else:
            steps = (v2ScaleFactor - v1ScaleFactor) / (v2xScreen - v1xScreen)

        # get heights relative to eye position of player (camera)
        ceiling = frontSector.ceilingHeight - self.player.getEyeZ()
        floor = frontSector.floorHeight - self.player.getEyeZ()

        ceilingStep = -(ceiling * steps)
        ceilingEnd = self.f_halfHeight - (ceiling * v1ScaleFactor)

        floorStep = -(floor * steps)
        floorStart = self.f_halfHeight - (floor * v1ScaleFactor)

        iXCurrent = v1xScreen
        while iXCurrent <= v2xScreen:
            drawStart = [iXCurrent + self.f_xOffset, ceilingEnd + self.f_yOffset]
            drawEnd = [iXCurrent + self.f_xOffset, floorStart + self.f_yOffset]
            self.game.drawLine(drawStart, drawEnd, rgba, 1)
            iXCurrent += 1
            ceilingEnd += ceilingStep
            floorStart += floorStep

    # Method in DOOM engine that calculated a wall height
    # scale factor given a distance of the wall from the screen
    # and the distance of that same angle from the player to screen
    def doomsolids_getScaleFactor(self, vxScreen, segToNormalAngle, distanceToNormal):
        # constants used with some issues for DOOM textures
        MAX_SCALEFACTOR = 64.0
        MIN_SCALEFACTOR = 0.00390625

        angle90 = Angle(90)
        screenXAngle = self.doomsolids_screenXToAngleLookup[vxScreen] # Angle object
        skewAngle = screenXAngle.addA(self.player.angle).subA(segToNormalAngle)

        # get scale factor
        screenXAngleCos = screenXAngle.getCos()
        skewAngleCos = skewAngle.getCos()
        scaleFactor = (self.f_distancePlayerToScreen * skewAngleCos) / (distanceToNormal * screenXAngleCos)

        # clamp
        scaleFactor = min(MAX_SCALEFACTOR, max(MIN_SCALEFACTOR, scaleFactor))
        return scaleFactor

    def doomsolids_angleToScreen(self, angle):
        ix = 0
        # TODO should these be 90 or fov?
        if angle.gtF(90):
            # left side
            a_newAngle = Angle(angle.deg - 90)
            ix = self.f_distancePlayerToScreen - round(a_newAngle.getTan() * self.f_halfWidth)
        else:
            # right side
            a_newAngle = Angle(90 - angle.deg)
            ix = round(a_newAngle.getTan() * self.f_halfWidth) + self.f_distancePlayerToScreen
        return int(ix)

    # needs to return 4 angles
    def doomsolids_clipVerticesToFov(self, v1, v2):
        a_fov = Angle(self.f_fov)

        v1Angle = self.player.angleToVertex(v1)
        v2Angle = self.player.angleToVertex(v2)

        a_spanAngle = v1Angle.subA(v2Angle)
        if a_spanAngle.gteF(self.f_fov * 2):
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
        v1AngleFromPlayer = v1Angle.subA(self.player.angle)
        v2AngleFromPlayer = v2Angle.subA(self.player.angle)
        # this puts their vertices around the 0 degree
        # left side of FOV is 45
        # right side of FOV = -45 (315)
        # if we rotate player to 45 then
        # left side is at 90
        # right side is at 0 (no negative comparisons)
        # if V1 is > 90 its outside
        # if V2 is < 0 its outside

        # v1 test:
        a_halfFov = a_fov.divF(2)
        a_v1Moved = v1AngleFromPlayer.addA(a_halfFov)
        if a_v1Moved.gtA(a_fov):
            # v1 is outside the fov
            # check if angle of v1 to v2 is also outside fov
            # by comparing how far v1 is away from fov
            # if more than dist v1 to v2 then the angle outside fov
            a_v1MovedAngle = a_v1Moved.subA(a_fov)
            if a_v1MovedAngle.gteA(a_spanAngle):
                return None

            # v2 is valid, clip v1
            v1AngleFromPlayer = a_halfFov.new()

        # v2 test: (we cant have angle < 0 so subtract angle from halffov)
        a_v2Moved = a_halfFov.subA(v2AngleFromPlayer)
        if a_v2Moved.gtA(a_fov):
            v2AngleFromPlayer = a_halfFov.neg()

        # rerotate angles
        v1AngleFromPlayer.iaddA(a_fov)
        v2AngleFromPlayer.iaddA(a_fov)

        return v1Angle, v2Angle, v1AngleFromPlayer, v2AngleFromPlayer

    # python DIY linked lists are a nightmare
    # because of the pass-object-by-reference
    # nature of variables
    # when I change next and prev values on a
    # node it changes it for that copy of the
    # variable, and not for the underlying reference
    # TODO take a seg and implement StoreWallRange
    # so that we can update the segs display range
    def doomsolids_clipWall(self, seg, segList, v1xScreen, v2xScreen, v1Angle, v2Angle, clippings, rangeRenderer):
        if len(segList) < 2:
            return

        segId = seg.ID
        segRange = None
        segIndex = None
        # skip all segments that end before this wall starts
        i=0
        while (i < len(segList) and segList[i].xEnd < v1xScreen - 1):
            i += 1
        segIndex = i
        segRange = segList[segIndex]

        # should always have a node since we cap our ends with
        # "infinity"
        # START to OVERLAP
        if v1xScreen < segRange.xStart:
            # found a position in the node list
            # are they overlapping?
            if v2xScreen < segRange.xStart - 1:
                # all of the wall is visible to insert it
                # STOREWALL
                # StoreWallRange(seg, CurrentWall.XStart, CurrentWall.XEnd);
                clippings[segId] = (v1xScreen, v2xScreen)
                rangeRenderer(seg, clippings[segId], v1Angle, v2Angle)
                segList.insert(segIndex, SolidSegmentRange(v1xScreen, v2xScreen))
                # go to next wall
                return
            # if not overlapping, end is already included
            # so just update the start
            # STOREWALL
            # StoreWallRange(seg, CurrentWall.XStart, FoundClipWall->XStart - 1);
            clippings[segId] = (v1xScreen,  segRange.xStart - 1)
            rangeRenderer(seg, clippings[segId], v1Angle, v2Angle)
            segRange.xStart = v1xScreen

        # FULL OVERLAPPED
        # this part is already occupied
        if v2xScreen <= segRange.xEnd:
            return # go to next wall

        # CHOP AND MERGE
        # start by looking at the next entry in the list
        # is the next entry within the current wall range?
        nextSegIndex = segIndex
        nextSegRange = segRange
        while v2xScreen >= segList[nextSegIndex + 1].xStart - 1:
            # STOREWALL
            # StoreWallRange(seg, NextWall->XEnd + 1, next(NextWall, 1)->XStart - 1);
            clippings[segId] = (nextSegRange.xEnd + 1,  segList[nextSegIndex + 1].xStart - 1)
            rangeRenderer(seg, clippings[segId], v1Angle, v2Angle)

            nextSegIndex += 1
            nextSegRange = segList[nextSegIndex]
            # partially clipped by other walls, store each fragment
            if v2xScreen <= nextSegRange.xEnd:
                segRange.xEnd = nextSegRange.xEnd
                if nextSegIndex != segIndex:
                    segIndex += 1
                    nextSegIndex += 1
                    del segList[segIndex:nextSegIndex]
                return

        # wall precedes all known segments
        # STOREWALL
        # StoreWallRange(seg, NextWall->XEnd + 1, CurrentWall.XEnd);
        clippings[segId] = (nextSegRange.xEnd + 1,  v2xScreen)
        rangeRenderer(seg, clippings[segId], v1Angle, v2Angle)
        segRange.xEnd = v2xScreen

        if (nextSegIndex != segIndex):
            segIndex += 1
            nextSegIndex += 1
            del segList[segIndex:nextSegIndex]
        return






    #################################
    ## DOOM PORTALS RENDER METHODS ##
    #################################

    def doomportals_render(self, onSegInspect = None):
        # optional function pointer when we inspect a visible seg
        self.onSegInspect = onSegInspect
        self.wallRenderer = self.doomportals_renderWall

        # clear our clipping list of walls
        self.segList = [SolidSegmentRange(-100000, -1)]
        self.segList.append(SolidSegmentRange(self.f_width, 100000))
        # clear our ceiling and floor clipping lists for portaled walls
        for i,v in enumerate(self.doomportals_ceilingClipHeight):
            self.doomportals_ceilingClipHeight[i] = -1; # reset
        for i,v in enumerate(self.doomportals_floorClipHeight):
            self.doomportals_floorClipHeight[i] = int(self.f_height)

        # render 3d viewport
        self.map.renderBspNodes(self.player.x, self.player.y, self.doomportals_renderSubsector)

    def doomportals_renderSubsector(self, subsector):
        # iterate segs in subsector
        for i in range(subsector.segCount):
            segId = subsector.firstSegID + i
            seg = self.map.segs[segId]
            linedef = seg.linedef

            v1 = seg.startVertex
            v2 = seg.endVertex
            # four angles
            angles = self.doomportals_clipVerticesToFov(v1, v2)

            if angles is not None:
                if self.onSegInspect is not None:
                    self.onSegInspect(seg, v1, v2)

                v1Angle = angles[0]
                v2Angle = angles[1]
                v1AngleFromPlayer = angles[2]
                v2AngleFromPlayer = angles[3]

                self.doomportals_addWallInFov(seg, v1Angle, v2Angle, v1AngleFromPlayer, v2AngleFromPlayer)

    def doomportals_addWallInFov(self, seg, v1Angle, v2Angle, v1AngleFromPlayer, v2AngleFromPlayer):
        v1 = seg.startVertex
        v2 = seg.endVertex

        # get screen projection Xs
        v1xScreen = self.doomportals_angleToScreen(v1AngleFromPlayer)
        v2xScreen = self.doomportals_angleToScreen(v2AngleFromPlayer)

        # skip same pixel wall
        if v1xScreen == v2xScreen:
            return

        # solid walls
        if seg.backSector == None:
            self.doomportals_clipSolidWall(seg, self.segList, v1xScreen, v2xScreen, v1Angle, v2Angle, self.wallRenderer)
            return

        # closed doors
        isCeilLess = seg.backSector.ceilingHeight <= seg.frontSector.floorHeight
        isFloorGreater = seg.backSector.floorHeight >= seg.frontSector.ceilingHeight
        if isCeilLess or isFloorGreater:
            self.doomportals_clipSolidWall(seg, self.segList, v1xScreen, v2xScreen, v1Angle, v2Angle, self.wallRenderer)
            return

        # windowed walls
        isCeilingDiff = seg.frontSector.ceilingHeight != seg.backSector.ceilingHeight;
        isFloorDiff = seg.frontSector.floorHeight != seg.backSector.floorHeight;
        if isCeilingDiff or isFloorDiff:
            self.doomportals_clipPortalWall(seg, self.segList, v1xScreen, v2xScreen, v1Angle, v2Angle, self.wallRenderer)
            return

    def doomportals_renderWall(self, seg, v1xScreen, v2xScreen, v1Angle, v2Angle):
        self.doomportals_calculateWallHeight(seg, v1xScreen, v2xScreen, v1Angle, v2Angle)

    class doomportals_FrameRenderData(object):
        def __init__(self):
            self.rgba = None

            self.f_distanceToV1 = 0
            self.f_distanceToNormal = 0
            self.f_v1ScaleFactor = 0
            self.f_v2ScaleFactor = 0
            self.f_steps = 0

            self.f_frontSectorCeiling = 0
            self.f_frontSectorFloor = 0
            self.f_ceilingStep = 0
            self.f_ceilingEnd = 0
            self.f_floorStep = 0
            self.f_floorStart = 0

            self.f_backSectorCeiling = 0
            self.f_backSectorFloor = 0

            self.b_drawUpperSection = False
            self.b_drawLowerSection = False

            self.f_upperHeightStep = 0
            self.i_upperHeight = 0
            self.f_lowerHeightStep = 0
            self.i_lowerHeight = 0

            self.b_updateFloor = False
            self.b_updateCeiling = False

    def doomportals_calculateWallHeight(self, seg, v1xScreen, v2xScreen, v1Angle, v2Angle):

        RD = FpsRenderer.doomportals_FrameRenderData()

        # get seg data
        v1 = seg.startVertex
        v2 = seg.endVertex

        # get texture color
        frontSidedef = seg.linedef.frontSidedef
        frontSector = frontSidedef.sector
        RD.rgba = self.getWallColor(frontSidedef.middleTexture, frontSector.lightLevel)

        # calculate distance to first edge of the wall
        angle90 = Angle(90)
        segToNormalAngle = Angle(seg.getAngle() + angle90.deg)
        normalToV1Angle = segToNormalAngle.subA(v1Angle)

        # normal angle is 90deg to wall
        segToPlayerAngle = angle90.subA(normalToV1Angle)

        RD.f_distanceToV1 = self.player.distanceToVertex(v1)
        RD.f_distanceToNormal = segToPlayerAngle.getSin() * RD.f_distanceToV1

        RD.f_v1ScaleFactor = self.doomportals_getScaleFactor(v1xScreen, segToNormalAngle, RD.f_distanceToNormal)
        RD.f_v2ScaleFactor = self.doomportals_getScaleFactor(v2xScreen, segToNormalAngle, RD.f_distanceToNormal)

        # screen xs can be the same so avoid div/0
        # if they are the same that means they occupy
        # one pixel
        # DIY tutorial (c++) does divide by zero
        # and when
        if v1xScreen == v2xScreen:
            RD.f_steps = 1
        else:
            RD.f_steps = (RD.f_v2ScaleFactor - RD.f_v1ScaleFactor) / (v2xScreen - v1xScreen)

        # portal walls
        RD.f_frontSectorCeiling = seg.frontSector.ceilingHeight - self.player.getEyeZ()
        RD.f_frontSectorFloor = seg.frontSector.floorHeight - self.player.getEyeZ()

        # get heights relative to eye position of player (camera)
        RD.f_ceilingStep = -(RD.f_frontSectorCeiling * RD.f_steps)
        RD.f_ceilingEnd = int(self.f_halfHeight - (RD.f_frontSectorCeiling * RD.f_v1ScaleFactor))

        RD.f_floorStep = -(RD.f_frontSectorFloor * RD.f_steps)
        RD.f_floorStart = int(self.f_halfHeight - (RD.f_frontSectorFloor * RD.f_v1ScaleFactor))

        # Handle Solid walls vs Portal Walls
        if seg.backSector:
            RD.f_backSectorCeiling = seg.backSector.ceilingHeight - self.player.getEyeZ()
            RD.f_backSectorFloor = seg.backSector.floorHeight - self.player.getEyeZ()

            self.doomportals_ceilingFloorUpdate(seg, RD)

            if RD.f_backSectorCeiling < RD.f_frontSectorCeiling:
                RD.b_drawUpperSection = True
                RD.f_upperHeightStep = -(RD.f_backSectorCeiling * RD.f_steps)
                RD.i_upperHeight = int(self.f_halfHeight - (RD.f_backSectorCeiling * RD.f_v1ScaleFactor))

            if RD.f_backSectorFloor > RD.f_frontSectorFloor:
                RD.b_drawLowerSection = True
                RD.f_lowerHeightStep = -(RD.f_backSectorFloor * RD.f_steps)
                RD.i_lowerHeight = int(self.f_halfHeight - (RD.f_backSectorFloor * RD.f_v1ScaleFactor))

        self.doomportals_renderSegment(seg, v1xScreen, v2xScreen, RD)

    # Method in DOOM engine that calculated a wall height
    # scale factor given a distance of the wall from the screen
    # and the distance of that same angle from the player to screen
    def doomportals_getScaleFactor(self, vxScreen, segToNormalAngle, distanceToNormal):
        # constants used with some issues for DOOM textures
        MAX_SCALEFACTOR = 64.0
        MIN_SCALEFACTOR = 0.00390625

        angle90 = Angle(90)
        screenXAngle = self.doomportals_screenXToAngleLookup[vxScreen] # Angle object
        skewAngle = screenXAngle.addA(self.player.angle).subA(segToNormalAngle)

        # get scale factor
        screenXAngleCos = screenXAngle.getCos()
        skewAngleCos = skewAngle.getCos()
        scaleFactor = (self.f_distancePlayerToScreen * skewAngleCos) / (distanceToNormal * screenXAngleCos)

        # clamp
        scaleFactor = min(MAX_SCALEFACTOR, max(MIN_SCALEFACTOR, scaleFactor))
        return scaleFactor

    def doomportals_angleToScreen(self, angle):
        ix = 0
        # TODO should these be 90 or fov?
        if angle.gtF(90):
            # left side
            a_newAngle = Angle(angle.deg - 90)
            ix = self.f_distancePlayerToScreen - round(a_newAngle.getTan() * self.f_halfWidth)
        else:
            # right side
            a_newAngle = Angle(90 - angle.deg)
            ix = round(a_newAngle.getTan() * self.f_halfWidth) + self.f_distancePlayerToScreen
        return int(ix)

    def doomportals_ceilingFloorUpdate(self, seg, RD):
        # RD is a reference so that is correct in we need to modify its contents
        if seg.backSector is None:
            RD.b_updateCeiling = True
            RD.b_updateFloor = True
            return

        RD.b_updateCeiling = RD.f_backSectorCeiling != RD.f_frontSectorCeiling
        RD.b_updateFloor = RD.f_backSectorFloor != RD.f_frontSectorFloor

        if seg.backSector.ceilingHeight <= seg.frontSector.floorHeight or seg.backSector.floorHeight >= seg.frontSector.ceilingHeight:
            # closed door
            RD.b_updateCeiling = True
            RD.b_updateFloor = True

        if seg.frontSector.ceilingHeight <= self.player.getEyeZ():
            # below view plane
            RD.b_updateCeiling = False

        if seg.frontSector.floorHeight >= self.player.getEyeZ():
            # above view plane
            RD.b_updateFloor = False

    def doomportals_renderSegment(self, seg, v1xScreen, v2xScreen, RD):
        iXCurrent = v1xScreen
        while iXCurrent <= v2xScreen:
            i_currentCeilingEnd = int(RD.f_ceilingEnd)
            i_currentFloorStart = int(RD.f_floorStart)

            # DIY code used a validate range method to clip and modify and continue
            # I cant pass ints by reference in Python so I am performing the function inline
            # if doomportals_validateRange(RD, iXCurrent, i_currentCeilingEnd, i_currentFloorStart) is False:
            #     continue
            # validateRange start
            if i_currentCeilingEnd < self.doomportals_ceilingClipHeight[iXCurrent] + 1:
                i_currentCeilingEnd = self.doomportals_ceilingClipHeight[iXCurrent] + 1
            if i_currentFloorStart >= self.doomportals_floorClipHeight[iXCurrent]:
                i_currentFloorStart = self.doomportals_floorClipHeight[iXCurrent] - 1

            if i_currentCeilingEnd > i_currentFloorStart:
                RD.f_ceilingEnd += RD.f_ceilingStep
                RD.f_floorStart += RD.f_floorStep
                iXCurrent += 1
                continue
            # validateRange end

            # is it a portal?
            if seg.backSector:
                self.doomportals_drawUpperSection(RD, iXCurrent, i_currentCeilingEnd)
                self.doomportals_drawLowerSection(RD, iXCurrent, i_currentFloorStart)
            else:
                # it is solid
                self.doomportals_drawMiddleSection(RD, iXCurrent, i_currentCeilingEnd, i_currentFloorStart)

            RD.f_ceilingEnd += RD.f_ceilingStep
            RD.f_floorStart += RD.f_floorStep

            iXCurrent += 1

    def doomportals_drawUpperSection(self, RD, iXCurrent, i_currentCeilingEnd):
        if RD.b_drawUpperSection:
            i_upperHeight = RD.i_upperHeight
            RD.i_upperHeight += RD.f_upperHeightStep

            if i_upperHeight >= self.doomportals_floorClipHeight[iXCurrent]:
                i_upperHeight = self.doomportals_floorClipHeight[iXCurrent] - 1

            if i_upperHeight >= i_currentCeilingEnd:
                # DRAW LINE
                drawStart = [iXCurrent + self.f_xOffset, i_currentCeilingEnd + self.f_yOffset]
                drawEnd = [iXCurrent + self.f_xOffset, i_upperHeight + self.f_yOffset]
                self.game.drawLine(drawStart, drawEnd, RD.rgba, 1)
                self.doomportals_ceilingClipHeight[iXCurrent] = i_upperHeight
            else:
                self.doomportals_ceilingClipHeight[iXCurrent] = i_currentCeilingEnd - 1
        else:
            self.doomportals_ceilingClipHeight[iXCurrent] = i_currentCeilingEnd - 1

    def doomportals_drawLowerSection(self, RD, iXCurrent, i_currentFloorStart):
        if RD.b_drawLowerSection:
            i_lowerHeight = RD.i_lowerHeight
            RD.i_lowerHeight += RD.f_lowerHeightStep

            if i_lowerHeight <= self.doomportals_ceilingClipHeight[iXCurrent]:
                i_lowerHeight = self.doomportals_ceilingClipHeight[iXCurrent] + 1

            if i_lowerHeight <= i_currentFloorStart:
                # DRAW LINE
                drawStart = [iXCurrent + self.f_xOffset, i_lowerHeight + self.f_yOffset]
                drawEnd = [iXCurrent + self.f_xOffset, i_currentFloorStart + self.f_yOffset]
                self.game.drawLine(drawStart, drawEnd, RD.rgba, 1)
                self.doomportals_floorClipHeight[iXCurrent] = i_lowerHeight
            else:
                self.doomportals_floorClipHeight[iXCurrent] = i_currentFloorStart + 1
        else:
            self.doomportals_floorClipHeight[iXCurrent] = i_currentFloorStart + 1

    def doomportals_drawMiddleSection(self, RD, iXCurrent, i_currentCeilingEnd, i_currentFloorStart):
        # DRAW LINE
        drawStart = [iXCurrent + self.f_xOffset, i_currentCeilingEnd + self.f_yOffset]
        drawEnd = [iXCurrent + self.f_xOffset, i_currentFloorStart + self.f_yOffset]
        self.game.drawLine(drawStart, drawEnd, RD.rgba, 1)
        self.doomportals_ceilingClipHeight[iXCurrent] = self.f_height # full clip
        self.doomportals_floorClipHeight[iXCurrent] = -1 # full clip

    # needs to return 4 angles
    def doomportals_clipVerticesToFov(self, v1, v2):
        a_fov = Angle(self.f_fov)

        v1Angle = self.player.angleToVertex(v1)
        v2Angle = self.player.angleToVertex(v2)

        a_spanAngle = v1Angle.subA(v2Angle)
        if a_spanAngle.gteF(self.f_fov * 2):
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
        v1AngleFromPlayer = v1Angle.subA(self.player.angle)
        v2AngleFromPlayer = v2Angle.subA(self.player.angle)
        # this puts their vertices around the 0 degree
        # left side of FOV is 45
        # right side of FOV = -45 (315)
        # if we rotate player to 45 then
        # left side is at 90
        # right side is at 0 (no negative comparisons)
        # if V1 is > 90 its outside
        # if V2 is < 0 its outside

        # v1 test:
        a_halfFov = a_fov.divF(2)
        a_v1Moved = v1AngleFromPlayer.addA(a_halfFov)
        if a_v1Moved.gtA(a_fov):
            # v1 is outside the fov
            # check if angle of v1 to v2 is also outside fov
            # by comparing how far v1 is away from fov
            # if more than dist v1 to v2 then the angle outside fov
            a_v1MovedAngle = a_v1Moved.subA(a_fov)
            if a_v1MovedAngle.gteA(a_spanAngle):
                return None

            # v2 is valid, clip v1
            v1AngleFromPlayer = a_halfFov.new()

        # v2 test: (we cant have angle < 0 so subtract angle from halffov)
        a_v2Moved = a_halfFov.subA(v2AngleFromPlayer)
        if a_v2Moved.gtA(a_fov):
            v2AngleFromPlayer = a_halfFov.neg()

        # rerotate angles
        v1AngleFromPlayer.iaddA(a_fov)
        v2AngleFromPlayer.iaddA(a_fov)

        return v1Angle, v2Angle, v1AngleFromPlayer, v2AngleFromPlayer

    # python DIY linked lists are a nightmare
    # because of the pass-object-by-reference
    # nature of variables
    # when I change next and prev values on a
    # node it changes it for that copy of the
    # variable, and not for the underlying reference
    # TODO take a seg and implement StoreWallRange
    # so that we can update the segs display range
    def doomportals_clipSolidWall(self, seg, segList, v1xScreen, v2xScreen, v1Angle, v2Angle, rangeRenderer):
        if len(segList) < 2:
            return

        segId = seg.ID
        segRange = None
        segIndex = None
        # skip all segments that end before this wall starts
        i=0
        while (i < len(segList) and segList[i].xEnd < v1xScreen - 1):
            i += 1
        segIndex = i
        segRange = segList[segIndex]

        # should always have a node since we cap our ends with
        # "infinity"
        # START to OVERLAP
        if v1xScreen < segRange.xStart:
            # found a position in the node list
            # are they overlapping?
            if v2xScreen < segRange.xStart - 1:
                # all of the wall is visible to insert it
                # STOREWALL
                # StoreWallRange(seg, CurrentWall.XStart, CurrentWall.XEnd);
                rangeRenderer(seg, v1xScreen, v2xScreen, v1Angle, v2Angle)
                segList.insert(segIndex, SolidSegmentRange(v1xScreen, v2xScreen))
                # go to next wall
                return
            # if not overlapping, end is already included
            # so just update the start
            # STOREWALL
            # StoreWallRange(seg, CurrentWall.XStart, FoundClipWall->XStart - 1);
            rangeRenderer(seg, v1xScreen,  segRange.xStart - 1, v1Angle, v2Angle)
            segRange.xStart = v1xScreen

        # FULL OVERLAPPED
        # this part is already occupied
        if v2xScreen <= segRange.xEnd:
            return # go to next wall

        # CHOP AND MERGE
        # start by looking at the next entry in the list
        # is the next entry within the current wall range?
        nextSegIndex = segIndex
        nextSegRange = segRange
        while v2xScreen >= segList[nextSegIndex + 1].xStart - 1:
            # STOREWALL
            # StoreWallRange(seg, NextWall->XEnd + 1, next(NextWall, 1)->XStart - 1);
            rangeRenderer(seg, nextSegRange.xEnd + 1,  segList[nextSegIndex + 1].xStart - 1, v1Angle, v2Angle)

            nextSegIndex += 1
            nextSegRange = segList[nextSegIndex]
            # partially clipped by other walls, store each fragment
            if v2xScreen <= nextSegRange.xEnd:
                segRange.xEnd = nextSegRange.xEnd
                if nextSegIndex != segIndex:
                    segIndex += 1
                    nextSegIndex += 1
                    del segList[segIndex:nextSegIndex]
                return

        # wall precedes all known segments
        # STOREWALL
        # StoreWallRange(seg, NextWall->XEnd + 1, CurrentWall.XEnd);
        rangeRenderer(seg, nextSegRange.xEnd + 1,  v2xScreen, v1Angle, v2Angle)
        segRange.xEnd = v2xScreen

        if (nextSegIndex != segIndex):
            segIndex += 1
            nextSegIndex += 1
            del segList[segIndex:nextSegIndex]
        return

    # Very similar to clipSolidWall but does not
    # modify the segList
    def doomportals_clipPortalWall(self, seg, segList, v1xScreen, v2xScreen, v1Angle, v2Angle, rangeRenderer):
        # find clip window
        segId = seg.ID
        segRange = None
        segIndex = None
        # skip all segments that end before this wall starts
        i=0
        while (i < len(segList) and segList[i].xEnd < v1xScreen - 1):
            i += 1
        segIndex = i
        segRange = segList[segIndex]

        # should always have a node since we cap our ends with
        # "infinity"
        # START to OVERLAP
        if v1xScreen < segRange.xStart:
            # found a position in the node list
            # are they overlapping?
            if v2xScreen < segRange.xStart - 1:
                # all of the wall is visible to insert it
                # STOREWALL
                # StoreWallRange(seg, CurrentWall.XStart, CurrentWall.XEnd);
                rangeRenderer(seg, v1xScreen, v2xScreen, v1Angle, v2Angle)
                # go to next wall
                return
            # if not overlapping, end is already included
            # so just update the start
            # STOREWALL
            # StoreWallRange(seg, CurrentWall.XStart, FoundClipWall->XStart - 1);
            rangeRenderer(seg, v1xScreen,  segRange.xStart - 1, v1Angle, v2Angle)

        # FULL OVERLAPPED
        # this part is already occupied
        if v2xScreen <= segRange.xEnd:
            return # go to next wall

        # CHOP AND MERGE
        # start by looking at the next entry in the list
        # is the next entry within the current wall range?
        nextSegIndex = segIndex
        nextSegRange = segRange
        while v2xScreen >= segList[nextSegIndex + 1].xStart - 1:
            # STOREWALL
            # StoreWallRange(seg, NextWall->XEnd + 1, next(NextWall, 1)->XStart - 1);
            rangeRenderer(seg, nextSegRange.xEnd + 1,  segList[nextSegIndex + 1].xStart - 1, v1Angle, v2Angle)

            nextSegIndex += 1
            nextSegRange = segList[nextSegIndex]
            # partially clipped by other walls, store each fragment
            if v2xScreen <= nextSegRange.xEnd:
                return

        # wall precedes all known segments
        # STOREWALL
        # StoreWallRange(seg, NextWall->XEnd + 1, CurrentWall.XEnd);
        rangeRenderer(seg, nextSegRange.xEnd + 1,  v2xScreen, v1Angle, v2Angle)





    #################################
    ## DOOM HISTORY RENDER METHODS ##
    #################################

    class doomhistory_FrameRenderData(object):
        def __init__(self):
            self.rgba = None

            self.f_distanceToV1 = 0
            self.f_distanceToNormal = 0
            self.f_v1ScaleFactor = 0
            self.f_v2ScaleFactor = 0
            self.f_steps = 0

            self.f_frontSectorCeiling = 0
            self.f_frontSectorFloor = 0
            self.f_ceilingStep = 0
            self.f_ceilingEnd = 0
            self.f_floorStep = 0
            self.f_floorStart = 0

            self.f_backSectorCeiling = 0
            self.f_backSectorFloor = 0

            self.b_drawUpperSection = False
            self.b_drawLowerSection = False

            self.f_upperHeightStep = 0
            self.i_upperHeight = 0
            self.f_lowerHeightStep = 0
            self.i_lowerHeight = 0

            self.b_updateFloor = False
            self.b_updateCeiling = False

    class doomhistory_FrameSegDrawData(object):
        def __init__(self):
            self.seg = None
            self.b_drawUpperSection = False
            self.b_drawMiddleSection = False
            self.b_drawLowerSection = False

            self.upperSection = []
            self.middleSection = []
            self.lowerSection = []

    class doomhistory_SingleDrawLine(object):
        def __init__(self):
            self.x1 = 0
            self.y1 = 0
            self.x2 = 0
            self.x2 = 0

    def doomhistory_render(self, lineMode = False, onSegInspect = None):
        # optional function pointer when we inspect a visible seg
        self.onSegInspect = onSegInspect
        self.wallRenderer = self.doomhistory_renderWall
        self.doomhistory_frameSegsDrawData.clear()
        self.doomhistory_lineMode = lineMode

        # clear our clipping list of walls
        self.segList = [SolidSegmentRange(-100000, -1)]
        self.segList.append(SolidSegmentRange(self.f_width, 100000))
        # clear our ceiling and floor clipping lists for portaled walls
        for i,v in enumerate(self.doomhistory_ceilingClipHeight):
            self.doomhistory_ceilingClipHeight[i] = -1; # reset
        for i,v in enumerate(self.doomhistory_floorClipHeight):
            self.doomhistory_floorClipHeight[i] = int(self.f_height)

        # render 3d viewport
        # This no longer draws but stores what to draw in the section lists of FrameSegDrawData
        self.map.renderBspNodes(self.player.x, self.player.y, self.doomhistory_renderSubsector)

        self.doomhistory_drawStoredSegs()

    def doomhistory_drawStoredSegs(self):
        for i,d in enumerate(self.doomhistory_frameSegsDrawData):
            frontSidedef = d.seg.linedef.frontSidedef
            frontSector = frontSidedef.sector
            if d.b_drawUpperSection:
                rgba = self.getWallColor(frontSidedef.upperTexture, frontSector.lightLevel)
                self.doomhistory_drawSection(d.upperSection, rgba)
            if d.b_drawMiddleSection:
                rgba = self.getWallColor(frontSidedef.middleTexture, frontSector.lightLevel)
                self.doomhistory_drawSection(d.middleSection, rgba)
            if d.b_drawLowerSection:
                rgba = self.getWallColor(frontSidedef.lowerTexture, frontSector.lightLevel)
                self.doomhistory_drawSection(d.lowerSection, rgba)

    def doomhistory_drawSection(self, sectionList, rgba):
        for i,line in enumerate(sectionList):
            drawStart = [line.x1 + self.f_xOffset, line.y1 + self.f_yOffset]
            drawEnd = [line.x2 + self.f_xOffset, line.y2 + self.f_yOffset]
            if self.doomhistory_lineMode:
                if i % 4 == 0:
                    self.game.drawLine(drawStart, drawEnd, rgba, 2)
            else:
                self.game.drawLine(drawStart, drawEnd, rgba, 1)

    def doomhistory_renderSubsector(self, subsector):
        # iterate segs in subsector
        for i in range(subsector.segCount):
            segId = subsector.firstSegID + i
            seg = self.map.segs[segId]
            linedef = seg.linedef

            v1 = seg.startVertex
            v2 = seg.endVertex
            # four angles
            angles = self.doomhistory_clipVerticesToFov(v1, v2)

            if angles is not None:
                if self.onSegInspect is not None:
                    self.onSegInspect(seg, v1, v2)

                v1Angle = angles[0]
                v2Angle = angles[1]
                v1AngleFromPlayer = angles[2]
                v2AngleFromPlayer = angles[3]

                self.doomhistory_addWallInFov(seg, v1Angle, v2Angle, v1AngleFromPlayer, v2AngleFromPlayer)

    def doomhistory_addWallInFov(self, seg, v1Angle, v2Angle, v1AngleFromPlayer, v2AngleFromPlayer):
        v1 = seg.startVertex
        v2 = seg.endVertex

        # get screen projection Xs
        v1xScreen = self.doomhistory_angleToScreen(v1AngleFromPlayer)
        v2xScreen = self.doomhistory_angleToScreen(v2AngleFromPlayer)

        # skip same pixel wall
        if v1xScreen == v2xScreen:
            return

        # solid walls
        if seg.backSector == None:
            self.doomhistory_clipSolidWall(seg, self.segList, v1xScreen, v2xScreen, v1Angle, v2Angle, self.wallRenderer)
            return

        # closed doors
        isCeilLess = seg.backSector.ceilingHeight <= seg.frontSector.floorHeight
        isFloorGreater = seg.backSector.floorHeight >= seg.frontSector.ceilingHeight
        if isCeilLess or isFloorGreater:
            self.doomhistory_clipSolidWall(seg, self.segList, v1xScreen, v2xScreen, v1Angle, v2Angle, self.wallRenderer)
            return

        # windowed walls
        isCeilingDiff = seg.frontSector.ceilingHeight != seg.backSector.ceilingHeight;
        isFloorDiff = seg.frontSector.floorHeight != seg.backSector.floorHeight;
        if isCeilingDiff or isFloorDiff:
            self.doomhistory_clipPortalWall(seg, self.segList, v1xScreen, v2xScreen, v1Angle, v2Angle, self.wallRenderer)
            return

    def doomhistory_renderWall(self, seg, v1xScreen, v2xScreen, v1Angle, v2Angle):
        self.doomhistory_calculateWallHeight(seg, v1xScreen, v2xScreen, v1Angle, v2Angle)

    def doomhistory_calculateWallHeight(self, seg, v1xScreen, v2xScreen, v1Angle, v2Angle):

        RD = FpsRenderer.doomhistory_FrameRenderData()

        # get seg data
        v1 = seg.startVertex
        v2 = seg.endVertex

        # get texture color
        frontSidedef = seg.linedef.frontSidedef
        frontSector = frontSidedef.sector
        RD.rgba = self.getWallColor(frontSidedef.middleTexture, frontSector.lightLevel)

        # calculate distance to first edge of the wall
        angle90 = Angle(90)
        segToNormalAngle = Angle(seg.getAngle() + angle90.deg)
        normalToV1Angle = segToNormalAngle.subA(v1Angle)

        # normal angle is 90deg to wall
        segToPlayerAngle = angle90.subA(normalToV1Angle)

        RD.f_distanceToV1 = self.player.distanceToVertex(v1)
        RD.f_distanceToNormal = segToPlayerAngle.getSin() * RD.f_distanceToV1

        RD.f_v1ScaleFactor = self.doomhistory_getScaleFactor(v1xScreen, segToNormalAngle, RD.f_distanceToNormal)
        RD.f_v2ScaleFactor = self.doomhistory_getScaleFactor(v2xScreen, segToNormalAngle, RD.f_distanceToNormal)

        # screen xs can be the same so avoid div/0
        # if they are the same that means they occupy
        # one pixel
        # DIY tutorial (c++) does divide by zero
        # and when
        if v1xScreen == v2xScreen:
            RD.f_steps = 1
        else:
            RD.f_steps = (RD.f_v2ScaleFactor - RD.f_v1ScaleFactor) / (v2xScreen - v1xScreen)

        # portal walls
        RD.f_frontSectorCeiling = seg.frontSector.ceilingHeight - self.player.getEyeZ()
        RD.f_frontSectorFloor = seg.frontSector.floorHeight - self.player.getEyeZ()

        # get heights relative to eye position of player (camera)
        RD.f_ceilingStep = -(RD.f_frontSectorCeiling * RD.f_steps)
        RD.f_ceilingEnd = int(self.f_halfHeight - (RD.f_frontSectorCeiling * RD.f_v1ScaleFactor))

        RD.f_floorStep = -(RD.f_frontSectorFloor * RD.f_steps)
        RD.f_floorStart = int(self.f_halfHeight - (RD.f_frontSectorFloor * RD.f_v1ScaleFactor))

        # Handle Solid walls vs Portal Walls
        if seg.backSector:
            RD.f_backSectorCeiling = seg.backSector.ceilingHeight - self.player.getEyeZ()
            RD.f_backSectorFloor = seg.backSector.floorHeight - self.player.getEyeZ()

            self.doomhistory_ceilingFloorUpdate(seg, RD)

            if RD.f_backSectorCeiling < RD.f_frontSectorCeiling:
                RD.b_drawUpperSection = True
                RD.f_upperHeightStep = -(RD.f_backSectorCeiling * RD.f_steps)
                RD.i_upperHeight = int(self.f_halfHeight - (RD.f_backSectorCeiling * RD.f_v1ScaleFactor))

            if RD.f_backSectorFloor > RD.f_frontSectorFloor:
                RD.b_drawLowerSection = True
                RD.f_lowerHeightStep = -(RD.f_backSectorFloor * RD.f_steps)
                RD.i_lowerHeight = int(self.f_halfHeight - (RD.f_backSectorFloor * RD.f_v1ScaleFactor))

        self.doomhistory_renderSegment(seg, v1xScreen, v2xScreen, RD)

    # Method in DOOM engine that calculated a wall height
    # scale factor given a distance of the wall from the screen
    # and the distance of that same angle from the player to screen
    def doomhistory_getScaleFactor(self, vxScreen, segToNormalAngle, distanceToNormal):
        # constants used with some issues for DOOM textures
        MAX_SCALEFACTOR = 64.0
        MIN_SCALEFACTOR = 0.00390625

        angle90 = Angle(90)
        screenXAngle = self.doomhistory_screenXToAngleLookup[vxScreen] # Angle object
        skewAngle = screenXAngle.addA(self.player.angle).subA(segToNormalAngle)

        # get scale factor
        screenXAngleCos = screenXAngle.getCos()
        skewAngleCos = skewAngle.getCos()
        scaleFactor = (self.f_distancePlayerToScreen * skewAngleCos) / (distanceToNormal * screenXAngleCos)

        # clamp
        scaleFactor = min(MAX_SCALEFACTOR, max(MIN_SCALEFACTOR, scaleFactor))
        return scaleFactor

    def doomhistory_angleToScreen(self, angle):
        ix = 0
        # TODO should these be 90 or fov?
        if angle.gtF(90):
            # left side
            a_newAngle = Angle(angle.deg - 90)
            ix = self.f_distancePlayerToScreen - round(a_newAngle.getTan() * self.f_halfWidth)
        else:
            # right side
            a_newAngle = Angle(90 - angle.deg)
            ix = round(a_newAngle.getTan() * self.f_halfWidth) + self.f_distancePlayerToScreen
        return int(ix)

    def doomhistory_ceilingFloorUpdate(self, seg, RD):
        # RD is a reference so that is correct in we need to modify its contents
        if seg.backSector is None:
            RD.b_updateCeiling = True
            RD.b_updateFloor = True
            return

        RD.b_updateCeiling = RD.f_backSectorCeiling != RD.f_frontSectorCeiling
        RD.b_updateFloor = RD.f_backSectorFloor != RD.f_frontSectorFloor

        if seg.backSector.ceilingHeight <= seg.frontSector.floorHeight or seg.backSector.floorHeight >= seg.frontSector.ceilingHeight:
            # closed door
            RD.b_updateCeiling = True
            RD.b_updateFloor = True

        if seg.frontSector.ceilingHeight <= self.player.getEyeZ():
            # below view plane
            RD.b_updateCeiling = False

        if seg.frontSector.floorHeight >= self.player.getEyeZ():
            # above view plane
            RD.b_updateFloor = False

    def doomhistory_renderSegment(self, seg, v1xScreen, v2xScreen, RD):
        # store our data we are going to draw instead of drawing it now
        segDrawData = FpsRenderer.doomhistory_FrameSegDrawData()
        segDrawData.seg = seg;
        segDrawData.b_drawUpperSection = RD.b_drawUpperSection
        segDrawData.b_drawMiddleSection = seg.backSector is None
        segDrawData.b_drawLowerSection = RD.b_drawLowerSection

        iXCurrent = v1xScreen
        while iXCurrent <= v2xScreen:
            i_currentCeilingEnd = int(RD.f_ceilingEnd)
            i_currentFloorStart = int(RD.f_floorStart)

            # DIY code used a validate range method to clip and modify and continue
            # I cant pass ints by reference in Python so I am performing the function inline
            # if doomhistory_validateRange(RD, iXCurrent, i_currentCeilingEnd, i_currentFloorStart) is False:
            #     continue
            # validateRange start
            if i_currentCeilingEnd < self.doomhistory_ceilingClipHeight[iXCurrent] + 1:
                i_currentCeilingEnd = self.doomhistory_ceilingClipHeight[iXCurrent] + 1
            if i_currentFloorStart >= self.doomhistory_floorClipHeight[iXCurrent]:
                i_currentFloorStart = self.doomhistory_floorClipHeight[iXCurrent] - 1

            if i_currentCeilingEnd > i_currentFloorStart:
                RD.f_ceilingEnd += RD.f_ceilingStep
                RD.f_floorStart += RD.f_floorStep
                iXCurrent += 1
                continue
            # validateRange end

            # is it a portal?
            if seg.backSector:
                self.doomhistory_drawUpperSection(RD, iXCurrent, i_currentCeilingEnd, segDrawData)
                self.doomhistory_drawLowerSection(RD, iXCurrent, i_currentFloorStart, segDrawData)
            else:
                # it is solid
                self.doomhistory_drawMiddleSection(RD, iXCurrent, i_currentCeilingEnd, i_currentFloorStart, segDrawData)

            RD.f_ceilingEnd += RD.f_ceilingStep
            RD.f_floorStart += RD.f_floorStep

            iXCurrent += 1

        # Save our draw data for this seg to the list
        if segDrawData.b_drawUpperSection or segDrawData.b_drawMiddleSection or segDrawData.b_drawLowerSection:
            self.doomhistory_frameSegsDrawData.append(segDrawData)

    def doomhistory_drawUpperSection(self, RD, iXCurrent, i_currentCeilingEnd, segDrawData):
        if RD.b_drawUpperSection:
            i_upperHeight = RD.i_upperHeight
            RD.i_upperHeight += RD.f_upperHeightStep

            if i_upperHeight >= self.doomhistory_floorClipHeight[iXCurrent]:
                i_upperHeight = self.doomhistory_floorClipHeight[iXCurrent] - 1

            if i_upperHeight >= i_currentCeilingEnd:
                # SAVE LINE FOR DRAW
                self.doomhistory_addLineToSection(segDrawData.upperSection, iXCurrent, i_currentCeilingEnd, i_upperHeight)
                self.doomhistory_ceilingClipHeight[iXCurrent] = i_upperHeight
            else:
                self.doomhistory_ceilingClipHeight[iXCurrent] = i_currentCeilingEnd - 1
        else:
            self.doomhistory_ceilingClipHeight[iXCurrent] = i_currentCeilingEnd - 1

    def doomhistory_drawLowerSection(self, RD, iXCurrent, i_currentFloorStart, segDrawData):
        if RD.b_drawLowerSection:
            i_lowerHeight = RD.i_lowerHeight
            RD.i_lowerHeight += RD.f_lowerHeightStep

            if i_lowerHeight <= self.doomhistory_ceilingClipHeight[iXCurrent]:
                i_lowerHeight = self.doomhistory_ceilingClipHeight[iXCurrent] + 1

            if i_lowerHeight <= i_currentFloorStart:
                # SAVE LINE FOR DRAW
                self.doomhistory_addLineToSection(segDrawData.lowerSection, iXCurrent, i_lowerHeight, i_currentFloorStart)
                self.doomhistory_floorClipHeight[iXCurrent] = i_lowerHeight
            else:
                self.doomhistory_floorClipHeight[iXCurrent] = i_currentFloorStart + 1
        else:
            self.doomhistory_floorClipHeight[iXCurrent] = i_currentFloorStart + 1

    def doomhistory_drawMiddleSection(self, RD, iXCurrent, i_currentCeilingEnd, i_currentFloorStart, segDrawData):
        # SAVE LINE FOR DRAW
        self.doomhistory_addLineToSection(segDrawData.middleSection, iXCurrent, i_currentCeilingEnd, i_currentFloorStart)
        self.doomhistory_ceilingClipHeight[iXCurrent] = self.f_height # full clip
        self.doomhistory_floorClipHeight[iXCurrent] = -1 # full clip

    def doomhistory_addLineToSection(self, sectionList, iXCurrent, i_currentCeilingEnd, i_currentFloorStart):
        line = FpsRenderer.doomhistory_SingleDrawLine()
        line.x1 = iXCurrent
        line.y1 = i_currentCeilingEnd
        line.x2 = iXCurrent
        line.y2 = i_currentFloorStart
        sectionList.append(line)

    # needs to return 4 angles
    def doomhistory_clipVerticesToFov(self, v1, v2):
        a_fov = Angle(self.f_fov)

        v1Angle = self.player.angleToVertex(v1)
        v2Angle = self.player.angleToVertex(v2)

        a_spanAngle = v1Angle.subA(v2Angle)
        if a_spanAngle.gteF(self.f_fov * 2):
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
        v1AngleFromPlayer = v1Angle.subA(self.player.angle)
        v2AngleFromPlayer = v2Angle.subA(self.player.angle)
        # this puts their vertices around the 0 degree
        # left side of FOV is 45
        # right side of FOV = -45 (315)
        # if we rotate player to 45 then
        # left side is at 90
        # right side is at 0 (no negative comparisons)
        # if V1 is > 90 its outside
        # if V2 is < 0 its outside

        # v1 test:
        a_halfFov = a_fov.divF(2)
        a_v1Moved = v1AngleFromPlayer.addA(a_halfFov)
        if a_v1Moved.gtA(a_fov):
            # v1 is outside the fov
            # check if angle of v1 to v2 is also outside fov
            # by comparing how far v1 is away from fov
            # if more than dist v1 to v2 then the angle outside fov
            a_v1MovedAngle = a_v1Moved.subA(a_fov)
            if a_v1MovedAngle.gteA(a_spanAngle):
                return None

            # v2 is valid, clip v1
            v1AngleFromPlayer = a_halfFov.new()

        # v2 test: (we cant have angle < 0 so subtract angle from halffov)
        a_v2Moved = a_halfFov.subA(v2AngleFromPlayer)
        if a_v2Moved.gtA(a_fov):
            v2AngleFromPlayer = a_halfFov.neg()

        # rerotate angles
        v1AngleFromPlayer.iaddA(a_fov)
        v2AngleFromPlayer.iaddA(a_fov)

        return v1Angle, v2Angle, v1AngleFromPlayer, v2AngleFromPlayer

    # python DIY linked lists are a nightmare
    # because of the pass-object-by-reference
    # nature of variables
    # when I change next and prev values on a
    # node it changes it for that copy of the
    # variable, and not for the underlying reference
    # TODO take a seg and implement StoreWallRange
    # so that we can update the segs display range
    def doomhistory_clipSolidWall(self, seg, segList, v1xScreen, v2xScreen, v1Angle, v2Angle, rangeRenderer):
        if len(segList) < 2:
            return

        segId = seg.ID
        segRange = None
        segIndex = None
        # skip all segments that end before this wall starts
        i=0
        while (i < len(segList) and segList[i].xEnd < v1xScreen - 1):
            i += 1
        segIndex = i
        segRange = segList[segIndex]

        # should always have a node since we cap our ends with
        # "infinity"
        # START to OVERLAP
        if v1xScreen < segRange.xStart:
            # found a position in the node list
            # are they overlapping?
            if v2xScreen < segRange.xStart - 1:
                # all of the wall is visible to insert it
                # STOREWALL
                # StoreWallRange(seg, CurrentWall.XStart, CurrentWall.XEnd);
                rangeRenderer(seg, v1xScreen, v2xScreen, v1Angle, v2Angle)
                segList.insert(segIndex, SolidSegmentRange(v1xScreen, v2xScreen))
                # go to next wall
                return
            # if not overlapping, end is already included
            # so just update the start
            # STOREWALL
            # StoreWallRange(seg, CurrentWall.XStart, FoundClipWall->XStart - 1);
            rangeRenderer(seg, v1xScreen,  segRange.xStart - 1, v1Angle, v2Angle)
            segRange.xStart = v1xScreen

        # FULL OVERLAPPED
        # this part is already occupied
        if v2xScreen <= segRange.xEnd:
            return # go to next wall

        # CHOP AND MERGE
        # start by looking at the next entry in the list
        # is the next entry within the current wall range?
        nextSegIndex = segIndex
        nextSegRange = segRange
        while v2xScreen >= segList[nextSegIndex + 1].xStart - 1:
            # STOREWALL
            # StoreWallRange(seg, NextWall->XEnd + 1, next(NextWall, 1)->XStart - 1);
            rangeRenderer(seg, nextSegRange.xEnd + 1,  segList[nextSegIndex + 1].xStart - 1, v1Angle, v2Angle)

            nextSegIndex += 1
            nextSegRange = segList[nextSegIndex]
            # partially clipped by other walls, store each fragment
            if v2xScreen <= nextSegRange.xEnd:
                segRange.xEnd = nextSegRange.xEnd
                if nextSegIndex != segIndex:
                    segIndex += 1
                    nextSegIndex += 1
                    del segList[segIndex:nextSegIndex]
                return

        # wall precedes all known segments
        # STOREWALL
        # StoreWallRange(seg, NextWall->XEnd + 1, CurrentWall.XEnd);
        rangeRenderer(seg, nextSegRange.xEnd + 1,  v2xScreen, v1Angle, v2Angle)
        segRange.xEnd = v2xScreen

        if (nextSegIndex != segIndex):
            segIndex += 1
            nextSegIndex += 1
            del segList[segIndex:nextSegIndex]
        return

    # Very similar to clipSolidWall but does not
    # modify the segList
    def doomhistory_clipPortalWall(self, seg, segList, v1xScreen, v2xScreen, v1Angle, v2Angle, rangeRenderer):
        # find clip window
        segId = seg.ID
        segRange = None
        segIndex = None
        # skip all segments that end before this wall starts
        i=0
        while (i < len(segList) and segList[i].xEnd < v1xScreen - 1):
            i += 1
        segIndex = i
        segRange = segList[segIndex]

        # should always have a node since we cap our ends with
        # "infinity"
        # START to OVERLAP
        if v1xScreen < segRange.xStart:
            # found a position in the node list
            # are they overlapping?
            if v2xScreen < segRange.xStart - 1:
                # all of the wall is visible to insert it
                # STOREWALL
                # StoreWallRange(seg, CurrentWall.XStart, CurrentWall.XEnd);
                rangeRenderer(seg, v1xScreen, v2xScreen, v1Angle, v2Angle)
                # go to next wall
                return
            # if not overlapping, end is already included
            # so just update the start
            # STOREWALL
            # StoreWallRange(seg, CurrentWall.XStart, FoundClipWall->XStart - 1);
            rangeRenderer(seg, v1xScreen,  segRange.xStart - 1, v1Angle, v2Angle)

        # FULL OVERLAPPED
        # this part is already occupied
        if v2xScreen <= segRange.xEnd:
            return # go to next wall

        # CHOP AND MERGE
        # start by looking at the next entry in the list
        # is the next entry within the current wall range?
        nextSegIndex = segIndex
        nextSegRange = segRange
        while v2xScreen >= segList[nextSegIndex + 1].xStart - 1:
            # STOREWALL
            # StoreWallRange(seg, NextWall->XEnd + 1, next(NextWall, 1)->XStart - 1);
            rangeRenderer(seg, nextSegRange.xEnd + 1,  segList[nextSegIndex + 1].xStart - 1, v1Angle, v2Angle)

            nextSegIndex += 1
            nextSegRange = segList[nextSegIndex]
            # partially clipped by other walls, store each fragment
            if v2xScreen <= nextSegRange.xEnd:
                return

        # wall precedes all known segments
        # STOREWALL
        # StoreWallRange(seg, NextWall->XEnd + 1, CurrentWall.XEnd);
        rangeRenderer(seg, nextSegRange.xEnd + 1,  v2xScreen, v1Angle, v2Angle)

