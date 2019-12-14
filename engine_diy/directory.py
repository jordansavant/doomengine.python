
class Directory(object):

    def __init__(self):
        self.lumpOffset = 0
        self.lumpSize = 0
        self.lumpName = ''

    def __str__(self):
        return "\
DIRECTORY\n\
 offset ....... {}\n\
 size ......... {}\n\
 name ......... {}\
".format(self.lumpOffset, self.lumpSize, self.lumpName)

