import hashlib

from app.file import File
import math


class Formatter:
    """FS formatting class to file space allocation and making a super block"""

    # init super block fields
    def __init__(self, hd_size=256, cluster_size=4096):
        """Init params of super block"""
        self.__record_size = 64
        self.__name = 'ATOS'
        self.__hd_size = hd_size * 1024 * 1024
        self.__cluster_size = cluster_size
        self.__clusters_count = self.__hd_size // self.__cluster_size
        self.__main_dir_size = math.ceil(1000 / (self.__cluster_size / self.__record_size)) * self.__cluster_size
        self.__fat_offset = self.__cluster_size
        self.__fat_copy_offset = self.__fat_offset + self.__clusters_count * 4
        self.__main_dir_offset = self.__fat_copy_offset + self.__clusters_count * 4
        self.__data_area_offset = self.__main_dir_offset + self.__main_dir_size
        first_cluster = self.__main_dir_offset//self.__cluster_size+1
        file = File(name='main_dir', mod='1111111', first_cluster=first_cluster, size=self.__main_dir_size)
        self.__main_dir = file

    def mk_super_block(self):
        """Make a byte string of super block"""
        super_block = bytes(self.__name, 'ansi')
        super_block += self.__cluster_size.to_bytes(2, byteorder='big')
        super_block += self.__clusters_count.to_bytes(4, byteorder='big')
        super_block += self.__hd_size.to_bytes(4, byteorder='big')
        super_block += self.__fat_offset.to_bytes(2, byteorder='big')
        super_block += self.__fat_copy_offset.to_bytes(4, byteorder='big')
        super_block += self.__main_dir.get_file_bytes()
        return super_block

    def mk_fat(self):
        count = self.__main_dir_offset // self.__cluster_size
        eng_clusters = (self.__clusters_count + 2).to_bytes(4, byteorder='big') * count
        start = count + 1
        main_dir_count = self.__main_dir_size // self.__cluster_size
        for i in range(start, start+main_dir_count-1):
            eng_clusters += (i+1).to_bytes(4, byteorder='big')
        eng_clusters += (self.__clusters_count + 1).to_bytes(4, byteorder='big') * 2
        users_cluster = len(eng_clusters) // 4
        eng_clusters += (0).to_bytes(4, byteorder='big') * (self.__clusters_count - count - main_dir_count - 1)
        return [users_cluster, eng_clusters]

    def formatting(self):
        """Create file of FS and fill it"""
        sb = self.mk_super_block()
        sb = sb + b' ' * (self.__cluster_size - len(sb))
        data = b'root' + b' ' * 10 + hashlib.md5(b'314ton').digest() + (1).to_bytes(1, byteorder='big') + \
               (1).to_bytes(1, byteorder='big')
        clust, fat = self.mk_fat()
        f = File('users', '', '0110100', clust, 1, data, '111')
        try:
            with open('../os.txt', 'wb') as file:
                file.write(sb)
                file.write(fat * 2)
                file.write(f.get_file_bytes() + b' ' * (self.__main_dir_size - len(f.get_file_bytes())))
                file.write(data + b' ' * (self.__hd_size - self.__data_area_offset - len(data)))
        except Exception:
            print('Something wrong!')
