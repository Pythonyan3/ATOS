from datetime import datetime


class File:

    def __init__(self, name='new_file', ext='', mod='0110100', first_cluster=1, uid=1, data='', attr='000', file_bytes=b''):
        if file_bytes:
            self.parse_bytes(file_bytes)
        else:
            self.name = name + ' ' * (32 - len(name))
            self.ext = ext + ' ' * (5 - len(ext))
            self.size = len(data)
            self.attr = attr
            self.mod = mod
            self.uid = uid
            self.creation_date = int(datetime.strftime(datetime.now(), "%Y%m%d%H%M%S"))
            self.modification_date = int(datetime.strftime(datetime.now(), "%Y%m%d%H%M%S"))
            self.first_cluster = first_cluster
            self.data = data

    def __str__(self):
        string = self.built_mod()
        string += '    ' + self.built_attr()
        string += '    ' + str(self.uid)
        string += '    ' + self.built_date()
        if self.ext.strip():
            string += ' ' + self.name.strip() + '.' + self.ext.strip()
        else:
            string += ' ' + self.name.strip()
        return string

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name + ' ' * (32 - len(name))

    @property
    def ext(self):
        return self.__ext

    @ext.setter
    def ext(self, ext):
        self.__ext = ext + ' ' * (5 - len(ext))

    @property
    def size(self):
        return self.__size

    @size.setter
    def size(self, size):
        self.__size = size

    @property
    def attr(self):
        return self.__attr

    @attr.setter
    def attr(self, attr):
        self.__attr = attr

    @property
    def mod(self):
        return self.__mod

    @mod.setter
    def mod(self, mod):
        self.__mod = mod

    @property
    def uid(self):
        return self.__uid

    @uid.setter
    def uid(self, uid):
        self.__uid = uid

    @property
    def creation_date(self):
        return self.__creation_date

    @creation_date.setter
    def creation_date(self, creation_date):
        self.__creation_date = creation_date

    @property
    def modification_date(self):
        return self.__modification_date

    @modification_date.setter
    def modification_date(self, modification_date):
        self.__modification_date = modification_date

    @property
    def first_cluster(self):
        return self.__first_cluster

    @first_cluster.setter
    def first_cluster(self, first_cluster):
        self.__first_cluster = first_cluster

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, data):
        self.__data = data

    @property
    def full_name(self):
        if self.ext.strip():
            return self.name.strip() + '.' + self.ext.strip()
        return self.name.strip()

    def is_dir(self):
        return int(self.mod[0])

    def get_file_bytes(self):
        """Return a record of file in bytes"""
        result = bytes(self.name, encoding='ansi') + bytes(self.ext, encoding='ansi')
        result += self.size.to_bytes(4, byteorder='big') + int(self.attr, 2).to_bytes(1, byteorder='big')
        result += int(self.mod, 2).to_bytes(1, byteorder='big') + self.uid.to_bytes(1, byteorder='big')
        result += self.creation_date.to_bytes(8, byteorder='big') + self.modification_date.to_bytes(8, byteorder='big')
        result += self.first_cluster.to_bytes(4, byteorder='big')
        return result

    def built_mod(self):
        ch = ['x', 'r', 'w']
        result = '-' if self.mod[0] == '0' else 'd'
        for i in range(1, len(self.mod)):
            result += '-' if self.mod[i] == '0' else ch[i % 3]
        return result

    def built_attr(self):
        ch = ['r', 's', 'h']
        result = ''
        for i in range(len(self.attr)):
            result += '-' if self.attr[i] == '0' else ch[i % 3]
        return result

    def built_date(self):
        date = str(self.modification_date)
        result = date[0:4] + '-' + date[4:6] + '-' + date[6:8] + ' '
        result += date[8:10] + ':' + date[10:12] + ':' + date[12: 14] + ' '
        return result

    def parse_bytes(self, file_bytes):
        self.name = str(file_bytes[:32], 'ansi')
        self.ext = str(file_bytes[32:37], 'ansi')
        self.size = int.from_bytes(file_bytes[37:41], byteorder='big')
        self.attr = bin(int.from_bytes(file_bytes[41:42], byteorder='big'))[2:]
        self.attr = '0' * (3 - len(self.attr)) + self.attr
        self.mod = bin(int.from_bytes(file_bytes[42:43], byteorder='big'))[2:]
        self.mod = '0' * (7 - len(self.mod)) + self.mod
        self.uid = int.from_bytes(file_bytes[43:44], byteorder='big')
        self.creation_date = int.from_bytes(file_bytes[44:52], byteorder='big')
        self.modification_date = int.from_bytes(file_bytes[52:60], byteorder='big')
        self.first_cluster = int.from_bytes(file_bytes[60:64], byteorder='big')
