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

import codecs, struct

class WADLoader(object):

    def __init__(self, wadpath):
        self.wadpath = wadpath;
        self.f = open(self.wadpath, 'rb') # read-binary

        self.loadHeader()

    def loadHeader(self):
        # The header has a total of 12 bytes (0x00 to 0x0b)
        # this 12-bytes is divided to 3 groups
        # first 4 bytes is the WAD type

        #self.f.seek(0)
        #self.header = self.f.read(4)
        #self.dircount = self.f.read(4)
        #self.diroffset = self.f.read(4)
        #self.type = self.read4bytes(0)
        self.dircount = self.read4bytes(4)
        self.diroffset = self.read4bytes(8)
        self.type = self.loadString(0, 4)
        self.dircount = self.loadInt(4, 4)
        self.diroffset = self.loadInt(8, 4)

        # convert to string
        #self.typestr = self.asstr(self.type)
        #self.dircounti = self.asint(self.dircount)

        #print(self.typestr, self.dircounti)
        #print(self.get4s(0), self.get4i(4))

    def loadString(self, offset, length):
        self.f.seek(offset)
        sss = ''
        for i in range(0, length):
            c = struct.unpack('<c', self.f.read(1))[0]
            sss += str(c, 'utf-8')
        return sss

    def loadInt(self, offset, length):
        self.f.seek(offset)
        ii = 0
        for i in range(0, length):
            buf = self.f.read(1)
            byte = int.from_bytes(buf, 'big')
            ii += (byte << (i * 8))
        return ii

    def __str__(self):
        return "\
WADLoader\n\
 WAD: {}\n\
 TYPE: {}\n\
 DIRS: {}\n\
 DOFFSET: {}\
 ".format(self.wadpath, self.type, self.dircount, self.diroffset)

