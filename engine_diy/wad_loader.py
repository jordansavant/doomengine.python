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
        self.type = self.read4bytes(0)
        self.dircount = self.read4bytes(4)
        self.diroffset = self.read4bytes(8)

        # convert to string
        self.typestr = self.asstr(self.type)
        self.dircounti = self.asint(self.dircount)

        print(self.typestr, self.dircounti)
        print(self.get4s(0), self.get4i(4))

    def asstr(self, arr):
        ss = ''
        for i, c in enumerate(arr):
            ss += chr(c)
        return ss

    def asint(self, arr):
        return sum(arr[i] << (i * 8) for i in range(len(arr)))
        #return (arr[3] << 24) + (arr[2] << 16) + (arr[1] << 8) + arr[0]

    def get4s(self, offset):
        self.f.seek(offset)
        ss = [0,0,0,0]
        sss = ''
        for i in range(0, 4):
            ss[i] = struct.unpack('<c', self.f.read(1))[0]
            sss += str(ss[i], 'utf-8')
        return sss
        return ss

    def get4i(self, offset):
        self.f.seek(offset)
        big = self.f.read(4) # big endian
        lil = struct.unpack_from('<I', big)
        return lil[0]

    # TODO load file into memory for faster access
    def read2bytes(self, offset):
        # get raw binary and convert from big-ending
        # to little-endian
        self.f.seek(offset)
        a = self.f.read(1)
        b = self.f.read(1)
        a = int.from_bytes(a, 'big')
        b = int.from_bytes(b, 'big')
        return [a, b]
        #return (b << 8) | a

    def read4bytes(self, offset):
        self.f.seek(offset)
        a = self.f.read(1)
        b = self.f.read(1)
        c = self.f.read(1)
        d = self.f.read(1)
        a = int.from_bytes(a, 'big')
        b = int.from_bytes(b, 'big')
        c = int.from_bytes(c, 'big')
        d = int.from_bytes(d, 'big')
        return [a, b, c, d]
        #return (d << 24) | (c << 16) | (b << 8) | a

    def __str__(self):
        return "\
WADLoader\n\
 WAD: {}\n\
 TYPE: {}\n\
 DIRS: {}\n\
 DOFFSET: {}\
 ".format(self.wadpath, self.typestr, self.dircount, self.diroffset)

