from file import File


class SuperBlock:

    def __init__(self, os_path):
        """Read params of super block from file and init super block object"""
        self.__record_size = 64
        with open(os_path, 'rb') as file:
            self.__name = str(file.read(4), 'ansi')
            self.__cluster_size = int.from_bytes(file.read(2), byteorder='big')
            self.__clusters_count = int.from_bytes(file.read(4), byteorder='big')
            self.__hd_size = int.from_bytes(file.read(4), byteorder='big')
            self.__fat_offset = int.from_bytes(file.read(2), byteorder='big')
            self.__fat_copy_offset = int.from_bytes(file.read(4), byteorder='big')
            self.__main_dir = File(file_bytes=file.read(self.record_size))

    @property
    def name(self):
        return self.__name

    @property
    def cluster_size(self):
        return self.__cluster_size

    @property
    def clusters_count(self):
        return self.__clusters_count

    @property
    def hd_size(self):
        return self.__hd_size

    @property
    def fat_offset(self):
        return self.__fat_offset

    @property
    def fat_copy_offset(self):
        return self.__fat_copy_offset

    @property
    def record_size(self):
        return self.__record_size

    @property
    def main_dir(self):
        return self.__main_dir
