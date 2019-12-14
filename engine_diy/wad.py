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
        self.type = self.loadString(0, 4) # char[]
        self.dircount = self.load_uint32(4) # uint32
        self.diroffset = self.load_uint32(8) # unit32

    def loadDirs(self):
        self.dirs = []
        for i in range(0, self.dircount):
            offset = self.diroffset + 16 * i
            # get dir info
            directory = Directory()
            directory.lumpOffset = self.load_uint32(offset)
            directory.lumpSize = self.load_uint32(offset + 4)
            directory.lumpName = self.loadString(offset + 8, 8)
            self.dirs.append(directory)

    def readVertexData(self, offset):
        v = Vertex()
        v.x = self.load_sshort(offset)
        v.y = self.load_sshort(offset + 2)
        return v

    def readLinedefData(self, offset):
        l = Linedef()
        l.startVertex = self.load_ushort(offset)
        l.endVertex = self.load_ushort(offset + 2)
        l.flags = self.load_ushort(offset + 4)
        l.lineType = self.load_ushort(offset + 6)
        l.sectorTag = self.load_ushort(offset + 8)
        l.frontSideDef = self.load_ushort(offset + 10)
        l.backSideDef = self.load_ushort(offset + 12)
        return l

    def findMapIndex(self, map):
        # non performant loop, need to make hashmap
        for i, d in enumerate(self.dirs):
            if d.lumpName == map.name:
                return i
        return -1

    def readMapVertex(self, map):
        mapIndex = self.findMapIndex(map)
        if mapIndex == -1:
            return False

        mapIndex += MapLumpsIndex.VERTEXES
        directory = self.dirs[mapIndex]
        if directory.lumpName != "VERTEXES":
            return False

        vertexBytes = 4
        verticesCount = int(directory.lumpSize / vertexBytes) # vertex size in bytes

        for i in range(0, verticesCount):
            vertex = self.readVertexData(directory.lumpOffset + i * vertexBytes)
            map.vertices.append(vertex)
            #print(vertex)

        return True

    def readMapLinedef(self, map):
        mapIndex = self.findMapIndex(map)
        if mapIndex == -1:
            return False

        mapIndex += MapLumpsIndex.LINEDEFS
        directory = self.dirs[mapIndex]
        if directory.lumpName != "LINEDEFS":
            return False

        linedefBytes = 14
        linedefCount = int(directory.lumpSize / linedefBytes)

        for i in range(0, linedefCount):
            linedef = self.readLinedefData(directory.lumpOffset + i * linedefBytes)
            map.linedefs.append(linedef)
            print(linedef)

        return True


    def loadMapData(self, map):
        if self.readMapVertex(map) == False:
            print("ERROR: Failed to load map vertices " + map.name)
            return False
        if self.readMapLinedef(map) == False:
            print("ERROR: Failed to load map linedefs " + map.name)
            return False
        return True

    def loadMap(self, mapName):
        map = Map()
        map.name = mapName
        return self.loadMapData(map)

    def loadString(self, offset, length, preserveNull = False):
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
