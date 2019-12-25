################### WAD CONTENTS #######################a
#
#                       <---- 32 bits  ---->
#                       /------------------\
#            --->  0x00 |  ASCII WAD Type  | 0X03
#            |          |------------------|
#    Header -|     0x04 | # of directories | 0x07
#            |          |------------------|
#            --->  0x08 | directory offset | 0x0B --
#            --->       |------------------| <--    |
#            |     0x0C |     Lump Data    |    |   |
#            |          |------------------|    |   |
#    Lumps - |          |        .         |    |   |
#            |          |        .         |    |   |
#            |          |        .         |    |   |
#            --->       |        .         |    |   |
#            --->       |------------------| <--|---
#            |          |    Lump offset   |    |
#            |          |------------------|    |
# Directory -|          | directory offset | ---
#    List    |          |------------------|
#            |          |    Lump Name     |
#            |          |------------------|
#            |          |        .         |
#            |          |        .         |
#            |          |        .         |
#            --->       \------------------/
#
# BIG-ENDIAN format

import struct
from engine_diy.map import *

class WAD(object):

    def __init__(self, wadpath):
        self.wadpath = wadpath;
        self.f = open(self.wadpath, 'rb') # read-binary

        self.loadHeader()
        self.loadDirs()

    def loadHeader(self):
        # The header has a total of 12 bytes (0x00 to 0x0b)
        # this 12-bytes is divided to 3 groups
        # first 4 bytes is the WAD type as CHAR
        # second 4 is count of directories as Int
        # third 4 is Int offset of directories
        self.type = self.load_string(0, 4) # char[]
        self.dircount = self.load_uint32(4) # uint32
        self.diroffset = self.load_uint32(8) # unit32

    def loadDirs(self):
        self.dirs = []
        self.dirMap = {}
        for i in range(0, self.dircount):
            offset = self.diroffset + 16 * i
            # get dir info
            directory = Directory()
            directory.lumpOffset = self.load_uint32(offset)
            directory.lumpSize = self.load_uint32(offset + 4)
            directory.lumpName = self.load_string(offset + 8, 8)
            self.dirs.append(directory)
            # keep hashmap of directory name to its index
            self.dirMap[directory.lumpName] = len(self.dirs) - 1

    # OBJECT LOADERS
    # objects are stored in lists in the WAD
    # and these methods take a single object
    # and create our map object
    def readVertexData(self, offset):
        v = Vertex()
        v.x = self.load_sshort(offset)
        v.y = self.load_sshort(offset + 2)
        return v

    def readLinedefData(self, offset):
        l = Linedef()
        l.startVertexID = self.load_ushort(offset)
        l.endVertexID = self.load_ushort(offset + 2)
        l.flags = self.load_ushort(offset + 4)
        l.lineType = self.load_ushort(offset + 6)
        l.sectorTag = self.load_ushort(offset + 8)
        l.frontSidedefID = self.load_ushort(offset + 10)
        l.backSidedefID = self.load_ushort(offset + 12)
        return l

    def readThingData(self, offset):
        t = Thing()
        t.x = self.load_sshort(offset)
        t.y = self.load_sshort(offset + 2)
        t.angle = self.load_ushort(offset + 4)
        t.type = self.load_ushort(offset + 6)
        t.flags = self.load_ushort(offset + 8)
        return t

    def readNodeData(self, offset):
        n = Node()
        n.xPartition = self.load_sshort(offset)
        n.yPartition = self.load_sshort(offset + 2)
        n.xChangePartition = self.load_sshort(offset + 4)
        n.yChangePartition = self.load_sshort(offset + 6)

        n.frontBoxTop = self.load_sshort(offset + 8)
        n.frontBoxBottom = self.load_sshort(offset + 10)
        n.frontBoxLeft = self.load_sshort(offset + 12)
        n.frontBoxRight = self.load_sshort(offset + 14)

        n.backBoxTop = self.load_sshort(offset + 16)
        n.backBoxBottom = self.load_sshort(offset + 18)
        n.backBoxLeft = self.load_sshort(offset + 20)
        n.backBoxRight = self.load_sshort(offset + 22)

        n.frontChildID = self.load_ushort(offset + 24)
        n.backChildID = self.load_ushort(offset + 26)
        return n

    def readSubsectorData(self, offset):
        ss = Subsector()
        ss.segCount = self.load_ushort(offset)
        ss.firstSegID = self.load_ushort(offset + 2)
        return ss

    def readSegData(self, offset):
        s = Seg()
        s.startVertexID = self.load_ushort(offset)
        s.endVertexID = self.load_ushort(offset + 2)
        s.angle = self.load_ushort(offset + 4)
        s.linedefID = self.load_ushort(offset + 6)
        s.direction = self.load_ushort(offset + 8)
        s.offset = self.load_ushort(offset + 10)
        return s

    def readSectorData(self, offset):
        s = Sector()
        s.floorHeight = self.load_sshort(offset)
        s.ceilingHeight = self.load_sshort(offset + 2)
        s.floorTexture = self.load_string(offset + 4, 8)
        s.ceilingTexture = self.load_string(offset + 12, 8)
        s.lightLevel = self.load_ushort(offset + 20)
        s.type = self.load_ushort(offset + 22)
        s.tag = self.load_ushort(offset + 24)
        return s

    def readSidedefData(self, offset):
        s = Sidedef()
        s.xOffset = self.load_sshort(offset)
        s.yOffset = self.load_sshort(offset + 2)
        s.upperTexture = self.load_string(offset + 4, 8)
        s.lowerTexture = self.load_string(offset + 12, 8)
        s.middleTexture = self.load_string(offset + 20, 8)
        s.sectorID = self.load_ushort(offset + 28)
        return s

    def findMapIndex(self, map):
        if map.name in self.dirMap:
            return self.dirMap[map.name] # get index
        return -1

    # LIST LOADER
    # Takes a pointer to a list location in
    # the WAD and loads the data into the
    # relevant map list
    def readMapDataList(self, map, indexOffset, lumpName, byteSize, reader, mapList):
        directory = self.dirs[indexOffset]
        if directory.lumpName != lumpName:
            return False

        count = int(directory.lumpSize / byteSize)
        for i in range(0, count):
            item = reader(directory.lumpOffset + i * byteSize)
            mapList.append(item)

        return True

    def loadMapData(self, map):
        mapIndex = self.findMapIndex(map)
        if mapIndex == -1:
            return False

        # load map data
        if self.readMapDataList(map, mapIndex + Map.Indices.VERTEXES, "VERTEXES", Vertex.sizeof(), self.readVertexData, map.vertices) is False:
            print("ERROR: Failed to load map vertices " + map.name)
            return False
        if self.readMapDataList(map, mapIndex + Map.Indices.LINEDEFS, "LINEDEFS", Linedef.sizeof(), self.readLinedefData, map.linedefs) is False:
            print("ERROR: Failed to load map linedefs " + map.name)
            return False
        if self.readMapDataList(map, mapIndex + Map.Indices.THINGS, "THINGS", Thing.sizeof(), self.readThingData, map.things) is False:
            print("ERROR: Failed to load map things " + map.name)
            return False
        if self.readMapDataList(map, mapIndex + Map.Indices.NODES, "NODES", Node.sizeof(), self.readNodeData, map.nodes) is False:
            print("ERROR: Failed to load map nodes " + map.name)
            return False
        if self.readMapDataList(map, mapIndex + Map.Indices.SSECTORS, "SSECTORS", Subsector.sizeof(), self.readSubsectorData, map.subsectors) is False:
            print("ERROR: Failed to load map subsectors " + map.name)
            return False
        if self.readMapDataList(map, mapIndex + Map.Indices.SEGS, "SEGS", Seg.sizeof(), self.readSegData, map.segs) is False:
            print("ERROR: Failed to load map segs " + map.name)
            return False
        if self.readMapDataList(map, mapIndex + Map.Indices.SECTORS, "SECTORS", Sector.sizeof(), self.readSectorData, map.sectors) is False:
            print("ERROR: Failed to load map sectors " + map.name)
            return False
        if self.readMapDataList(map, mapIndex + Map.Indices.SIDEDEFS, "SIDEDEFS", Sidedef.sizeof(), self.readSidedefData, map.sidedefs) is False:
            print("ERROR: Failed to load map sidedefs " + map.name)
            return False

        # run some helpers to define the map
        map.createData()

        return True

    def loadMap(self, mapName):
        map = Map()
        map.name = mapName
        if self.loadMapData(map):
            return map
        return None

    # DATA TYPE LOADERS
    # Gets raw byte data from WAD
    # in expected format
    def load_string(self, offset, length, preserveNull = False):
        self.f.seek(offset)
        sss = ''
        for i in range(0, length):
            c = struct.unpack('<c', self.f.read(1))[0]
            if ord(c) != 0:
                sss += str(c, 'ascii')
        return sss

    def load_sshort(self, offset):
        self.f.seek(offset)
        f = self.f.read(2)
        return struct.unpack('<h', f)[0]

    def load_ushort(self, offset):
        self.f.seek(offset)
        f = self.f.read(2)
        return struct.unpack('<H', f)[0]

    def load_uint32(self, offset):
        self.f.seek(offset)
        f = self.f.read(4)
        return struct.unpack('<I', f)[0]

    def info(self, dirs=False):
        wad = "\
WAD\n\
 path ......... {}\n\
 type ......... {}\n\
 dir_count .... {}\n\
 dir_offset ... {}\n\
 dir_1 ........ {}\n\
 dir_2 ........ {}\n\
 dir_3 ........ {}\
".format(self.wadpath, self.type, self.dircount, self.diroffset, self.dirs[0].lumpName, self.dirs[1].lumpName, self.dirs[2].lumpName)
        if dirs:
            wad += "\n"
            for i, d in enumerate(self.dirs):
                wad += str(d) + "\n"
        return wad

class Directory(object):
    def __init__(self):
        self.lumpOffset = 0 # uint32
        self.lumpSize = 0 # uint32
        self.lumpName = '' # char[8]
    def __str__(self):
        return (\
            "DIRECTORY\n" +\
            " offset ....... {}\n" + \
            " size ......... {}\n" + \
            " name ......... {}\n"\
        ).format(self.lumpOffset, self.lumpSize, self.lumpName)
