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
        self.type = self.loadString(0, 4)
        self.dircount = self.loadInt(4, 4)
        self.diroffset = self.loadInt(8, 4)

    def loadDirs(self):
        self.dirs = []
        lumpOffset = self.loadInt(self.diroffset, 4)
        lumpSize = self.loadInt(self.diroffset + 4, 4)
        for i in range(0, self.dircount):
            # get dir info
            offset = self.diroffset + 16 * i
            lumpOffset = self.loadInt(offset, 4)
            lumpSize = self.loadInt(offset + 4, 4)
            lumpName = self.loadString(offset + 8, 8)
            directory = Directory(lumpOffset, lumpSize, lumpName)
            self.dirs.append(directory)

    def loadString(self, offset, length, preserveNull = False):
        self.f.seek(offset)
        sss = ''
        for i in range(0, length):
            c = struct.unpack('<c', self.f.read(1))[0]
            if ord(c) != 0:
                sss += str(c, 'ascii')
        return sss

    def loadInt(self, offset, length):
        self.f.seek(offset)
        ii = 0
        for i in range(0, length):
            buf = self.f.read(1)
            byte = int.from_bytes(buf, 'big')
            ii += (byte << (i * 8))
        return ii

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

    def __init__(self, lumpOffset, lumpSize, lumpName):
        self.lumpOffset = lumpOffset
        self.lumpSize = lumpSize
        self.lumpName = lumpName


    def __str__(self):
        return "\
DIRECTORY\n\
 offset ....... {}\n\
 size ......... {}\n\
 name ......... {}\
".format(self.lumpOffset, self.lumpSize, self.lumpName)
