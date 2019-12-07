from datetime import datetime
import math
import os
import hashlib
import exeptions
from formatter import Formatter
from user import User
from termcolor import colored
from superblock import SuperBlock
from file import File


class Atos:

    def __init__(self, os_path='os.txt'):
        if not os.path.isfile(os_path):
            self.fs_formatting()
        self.super_block = SuperBlock(os_path)
        self.location = ''
        self.users = self.load_users()
        self.user = None

    @property
    def location(self):
        return self.__location

    @location.setter
    def location(self, location):
        self.__location = location

    """System calls"""

    def make_file(self, path, mod='0110100', data='', attr='000'):
        """Make a new file"""
        path, name = self.slice_path(path)  # slice path and name
        directory = self.check_dir_w_permission(path)
        if self.read_directory(directory).get(name):  # check existed files
            raise exeptions.FSExeption('File with name "{}" is already exist!'.format(name))
        name, ext = self.parse_file_name(name)  # parse file name
        count = self.get_cluster_count(data)  # get required cluster's count
        clusters = self.get_free_clusters(count)    # get numbers of free clusters
        self.set_cluster_engaged(clusters)
        size = len(data) if mod[0] == '0' else self.super_block.cluster_size * len(clusters)
        self.write_record(File(name, ext, mod, clusters[0], self.user.id, attr, size), directory, path)
        self.write_data(clusters, bytes(data, 'ansi'))

    def remove_file(self, path):
        """Remove file or directory"""
        # full_path = self.path_conversion(path)
        path, name = self.slice_path(path)
        file, directory = self.check_file_w_permission(path, name)
        if file.is_dir():
            for f in self.read_directory(file).values():
                try:
                    self.remove_file(path + '/' + name + '/' + f.full_name.strip())
                except exeptions.FSExeption:
                    print(colored('{}: Permission denied!'.format(f.full_name.strip()), 'red'))
            if not self.read_directory(file).values():
                self.remove_record(file, directory)
                clusters = self.get_clusters_seq(file.first_cluster)
                self.set_clusters_free(clusters)
        else:
            self.remove_record(file, directory)
            clusters = self.get_clusters_seq(file.first_cluster)
            self.set_clusters_free(clusters)

    def move_file(self, source_path, target_path):
        """Moves file (also rename)"""
        source_path, source_name = self.slice_path(source_path)
        source_file, source_directory = self.check_file_w_permission(source_path, source_name)
        target_path, target_name = self.slice_path(target_path)
        target_directory = self.check_dir_w_permission(target_path)
        if (target_path + '/').rfind(source_path + '/' + source_name + '/') > -1:
            raise exeptions.FSExeption('Cannot move file into itself!')
        files = self.read_directory(target_directory)
        if (source_path != target_path or source_name != target_name) and files.get(target_name):
            raise exeptions.FSExeption('File with name "{}" is already exist!'.format(target_name))
        self.remove_record(source_file, source_directory)
        source_file.name, source_file.ext = self.parse_file_name(target_name)
        self.write_record(source_file, target_directory, target_path)

    def copy_file(self, source_full_path, target_full_path):
        """Makes a copy of file or directory"""
        source_path, source_name = self.slice_path(source_full_path)
        source_file, source_directory = self.check_file_r_permission(source_path, source_name)
        self.check_dir_x_permission(source_path)    # check x permission
        target_path, target_name = self.slice_path(target_full_path)
        target_directory = self.check_dir_w_permission(target_path)
        if (target_path + '/').rfind(source_path + '/' + source_name + '/') > -1:
            raise exeptions.FSExeption('Cannot copy file into itself!')
        files = self.read_directory(target_directory)
        if source_full_path != target_full_path and files.get(target_name):
            raise exeptions.FSExeption('File with name "{}" is already exist!'.format(target_name))
        elif source_full_path == target_full_path and files.get(target_name):
            target_name = self.get_copy_name(target_name, files)
        if source_file.is_dir():
            self.check_dir_x_permission(source_full_path)
            files = self.read_directory(source_file).values()
            self.parse_file_name(target_name)  # check len of name and extension
            self.make_file(target_path + '/' + target_name, source_file.mod, '', source_file.attr)
            for file in files:
                new_source_path = source_full_path + '/' + file.full_name
                new_target_path = target_path + '/' + target_name + '/' + file.full_name
                try:
                    self.copy_file(new_source_path, new_target_path)
                except exeptions.FSExeption as e:
                    print(colored(e, 'red'))
        else:
            data = self.read_file(source_file)
            self.parse_file_name(target_name)   # check len of name and extension
            self.make_file(target_path + '/' + target_name, source_file.mod, str(data, 'ansi'), source_file.attr)

    def change_directory(self, path):
        """Changes user's location"""
        path = self.path_conversion(path)
        self.check_dir_x_permission(path)
        self.location = path

    def show_directory(self, path):
        """Returns files of directory and x permission"""
        path = self.path_conversion(path)
        directory = self.check_dir_r_permission(path)
        try:
            self.check_dir_x_permission(path)
            files = self.read_directory(directory).values()
            return [value for value in files if value.attr[2] == '0' or self.user.role]
        except exeptions.FSExeption:
            files = self.read_directory(directory).items()
            return [key for key, value in files if value.attr[2] != '1']

    def login(self, login, password):
        """Authorization"""
        user = self.users.get(login)
        if user and user.password == hashlib.md5(bytes(password, 'ansi')).digest() and user.id != 0:
            self.user = user
        else:
            raise exeptions.FSExeption('Incorrect login or password!')

    def logout(self):
        """Logout"""
        self.location = ''
        self.user = None

    def users_list(self):
        return [user for user in self.users.values() if user.id]

    def make_user(self, login, password, role):
        """Makes user account"""
        if not self.user.role:
            raise exeptions.FSExeption('{}: Permission denied!'.format(self.user.login.strip()))
        if self.users.get(login.strip()):
            raise exeptions.FSExeption('User with login "{}", already exist!'.format(login.strip()))
        password = hashlib.md5(bytes(password, 'ansi')).digest()
        user = User(login=login.strip(), password=password, role=int(role), id=len(self.users) + 1)
        self.users[user.login.strip()] = user
        self.save_users()

    def remove_user(self, login):
        """Blocks user account"""
        login = login.strip()
        if not self.users.get(login):
            raise exeptions.FSExeption('User with login "{}" not found!'.format(login))
        if not self.user.role or login == 'root' or self.user.login.strip() == login:
            raise exeptions.FSExeption('{}: Permission denied!'.format(self.user.login.strip()))
        self.users[login.strip()].id = 0
        self.save_users()

    def change_mod(self, path, mod):
        """Changes file's mode (permissions)"""
        full_path, full_name = self.slice_path(path)
        rwx, rsh, directory = self.get_directory(full_path)
        file = self.read_directory(directory).get(full_name)
        if not file:
            raise exeptions.FSExeption('No such file or directory!')
        if file.uid != self.user.id and not self.user.role:
            raise exeptions.FSExeption('{}: Permission denied!'.format(self.user.login.strip()))
        file.mod = file.mod[:1] + self.get_binary(int(mod[0])) + self.get_binary(int(mod[1]))
        self.rewrite_record(file, directory)

    def change_attr(self, path, attr):
        """Changes file's attributes"""
        full_path, full_name = self.slice_path(path)
        rwx, rsh, directory = self.get_directory(full_path)
        file = self.read_directory(directory).get(full_name)
        if not file:
            raise exeptions.FSExeption('No such file or directory!')
        if file.uid != self.user.id and not self.user.role:
            raise exeptions.FSExeption('{}: Permissions denied!'.format(self.user.login.strip()))
        file.attr = self.get_binary(int(attr))
        self.rewrite_record(file, directory)

    def open(self, path):
        """Opens and reads file"""
        path, name = self.slice_path(path)
        file, directory = self.check_file_r_permission(path, name)
        if file.is_dir():
            raise exeptions.FSExeption('{}: File not found!'.format(name))
        return str(self.read_file(file), encoding='ansi')

    def write(self, path, data):
        """Writes data into file"""
        path, name = self.slice_path(path)
        file, directory = self.check_file_w_permission(path, name)
        clusters = self.get_clusters_seq(file.first_cluster)
        req_clusters_count = math.ceil(len(data) / self.super_block.cluster_size)
        if req_clusters_count != len(clusters):
            clusters = self.change_clusters_count(clusters, req_clusters_count)
        file.modification_date = int(datetime.strftime(datetime.now(), "%Y%m%d%H%M%S"))
        file.size = len(data)
        self.write_data(clusters, bytes(data, 'ansi'))
        self.rewrite_record(file, directory)

    def append(self, path, data):
        """Appends data to the end of the file"""
        path, name = self.slice_path(path)
        file, directory = self.check_file_w_permission(path, name)
        clusters = self.get_clusters_seq(file.first_cluster)
        old_data = self.read_file(file)
        old_data = old_data + b'\n' if old_data else old_data
        data = old_data + bytes(data, 'ansi')
        req_clusters_count = math.ceil(len(data) / self.super_block.cluster_size)
        if req_clusters_count != len(clusters):
            clusters = self.change_clusters_count(clusters, req_clusters_count)
        file.modification_date = int(datetime.strftime(datetime.now(), "%Y%m%d%H%M%S"))
        file.size = len(data)
        self.write_data(clusters, data)
        self.rewrite_record(file, directory)

    def fs_formatting(self, hd_size=256, cluster_size=4096):
        """Format FS"""
        if 20 <= hd_size <= 1024 and (not cluster_size & (cluster_size - 1) and 512 <= cluster_size <= 32768):
            formatter = Formatter(hd_size, cluster_size)
            formatter.formatting()
            self.__init__()
        else:
            raise exeptions.FSExeption("Incorrect HD size or cluster's size!")

    """System functions"""

    def write_permission(self, path):
        """Check w permission for write append functions only"""
        path, name = self.slice_path(path)
        self.check_file_w_permission(path, name)

    def get_free_clusters(self, count=1):
        """Getting numbers of free clusters. Return a list of free clusters numbers"""
        clusters = list()
        main_dir_clusters_count = self.super_block.main_dir.size // self.super_block.cluster_size - 1
        offset = self.super_block.fat_offset + (self.super_block.main_dir.first_cluster + main_dir_clusters_count) * 4
        with open('os.txt', 'r+b') as file:
            file.seek(offset)
            while len(clusters) < count and file.tell() != self.super_block.fat_copy_offset:
                if int.from_bytes(file.read(4), byteorder='big') == 0:
                    clusters.append(((file.tell() - self.super_block.fat_offset) // 4))
        if len(clusters) == count:
            return clusters
        raise exeptions.FSExeption('Memory is out!')

    def get_clusters_seq(self, first_cluster):
        """Returns clusters sequence of a file"""
        result = [first_cluster]
        with open('os.txt', 'rb') as file:
            file.seek(self.super_block.fat_offset + (first_cluster - 1) * 4)
            num = int.from_bytes(file.read(4), byteorder='big')
            while num != self.super_block.clusters_count + 1:
                result.append(num)
                file.seek(self.super_block.fat_offset + (num - 1) * 4)
                num = int.from_bytes(file.read(4), byteorder='big')
        return result

    def get_cluster_count(self, data):
        """Return a count of required clusters"""
        if data:
            return math.ceil(len(data) / self.super_block.cluster_size)
        return 1

    def set_cluster_engaged(self, clusters):
        """Set cluster's status engaged"""
        with open('os.txt', 'r+b') as file:
            for i in range(len(clusters)-1):
                # write in FAT
                file.seek(self.super_block.fat_offset + (clusters[i] - 1) * 4)
                file.write(clusters[i+1].to_bytes(4, byteorder='big'))
                # write in FAT copy
                file.seek(self.super_block.fat_copy_offset + (clusters[i] - 1) * 4)
                file.write(clusters[i + 1].to_bytes(4, byteorder='big'))
            # write in FAT last cluster
            file.seek(self.super_block.fat_offset + (clusters[-1] - 1) * 4)
            file.write((self.super_block.clusters_count + 1).to_bytes(4, byteorder='big'))
            # write in FAT copy last cluster
            file.seek(self.super_block.fat_copy_offset + (clusters[-1] - 1) * 4)
            file.write((self.super_block.clusters_count + 1).to_bytes(4, byteorder='big'))

    def set_clusters_free(self, clusters):
        """Set cluster's status free"""
        with open('os.txt', 'r+b') as file:
            for cluster in clusters:
                # write in FAT
                file.seek(self.super_block.fat_offset + (cluster - 1) * 4)
                file.write((0).to_bytes(4, byteorder='big'))
                # write in FAT copy
                file.seek(self.super_block.fat_copy_offset + (cluster - 1) * 4)
                file.write((0).to_bytes(4, byteorder='big'))

    def change_clusters_count(self, clusters, req_clusters_count):
        """Remove or add clusters to clusters sequence of a file. Returns clusters sequence"""
        if req_clusters_count > len(clusters):
            count = req_clusters_count - len(clusters)
            clusters += self.get_free_clusters(count)
            if len(clusters) >= 2:
                self.set_cluster_engaged(clusters[-2:])
            else:
                self.set_cluster_engaged(clusters)
        else:
            count = len(clusters) - req_clusters_count
            self.set_clusters_free(clusters[count:])
            clusters = clusters[:count]
            self.set_cluster_engaged(clusters)
        return clusters

    def read_directory(self, f):
        """Returns a dict of files"""
        result = dict()
        clusters = self.get_clusters_seq(f.first_cluster)
        with open('os.txt', 'rb') as file:
            offset = (clusters.pop(0) - 1) * self.super_block.cluster_size
            file.seek(offset)
            while True:
                if file.tell() >= offset + self.super_block.cluster_size:
                    if not clusters:
                        break
                    offset = (clusters.pop(0)-1) * self.super_block.cluster_size
                    file.seek(offset)
                record = file.read(self.super_block.record_size)
                if not record.rstrip():
                    break
                if record[:1] != b' ':
                    f = File(file_bytes=record)
                    result[f.full_name] = f
        return result

    def read_file(self, f):
        """Returns file's data"""
        data = b''
        clusters = self.get_clusters_seq(f.first_cluster)
        with open('os.txt', 'rb') as file:
            for cluster in clusters:
                file.seek((cluster-1) * self.super_block.cluster_size)
                data += file.read(self.super_block.cluster_size)
        return data.rstrip()

    def get_directory(self, path):
        """Returns permissions and File object of required directory"""
        rwx = 7
        rsh = 0
        path_list = path.split('/')
        path_list.pop(0)
        directory = self.super_block.main_dir
        files = self.read_directory(directory)
        for name in path_list:
            directory = files.get(name)
            if directory and directory.is_dir():
                rwx = self.get_mod(directory) & rwx
                rsh = self.get_attr(directory) | rsh
                files = self.read_directory(directory)
            else:
                raise exeptions.FSExeption('Directory not found!')
        return [rwx, rsh, directory]

    def write_record(self, f, directory, dir_path=''):
        """Write a file record"""
        clusters = self.get_clusters_seq(directory.first_cluster)
        with open('os.txt', 'r+b') as file:
            offset = (clusters.pop(0) - 1) * self.super_block.cluster_size
            file.seek(offset)
            while True:
                if file.tell() == offset + self.super_block.cluster_size:
                    if clusters:
                        offset = (clusters.pop(0) - 1) * self.super_block.cluster_size
                        file.seek(offset)
                    else:
                        clusters = self.get_clusters_seq(directory.first_cluster)
                        clusters = self.change_clusters_count(clusters, len(clusters) + 1)
                        p_path = dir_path[:dir_path.rfind('/')]
                        p_dir = self.check_dir_w_permission(p_path)
                        directory.size = directory.size + self.super_block.cluster_size
                        self.rewrite_record(directory, p_dir)
                        offset = (clusters[-1] - 1) * self.super_block.cluster_size
                        file.seek(offset)
                record = file.read(self.super_block.record_size)
                if record[:1] == b' ':
                    file.seek(-self.super_block.record_size, 1)
                    file.write(f.get_file_bytes())
                    return True

    def rewrite_record(self, f, directory):
        """Rewrite a file record"""
        clusters = self.get_clusters_seq(directory.first_cluster)
        with open('os.txt', 'r+b') as file:
            offset = (clusters.pop(0) - 1) * self.super_block.cluster_size
            file.seek(offset)
            while True:
                if file.tell() == offset + self.super_block.cluster_size:
                    if clusters:
                        offset = (clusters.pop(0) - 1) * self.super_block.cluster_size
                        file.seek(offset)
                    else:
                        return None
                fil = File(file_bytes=file.read(self.super_block.record_size))
                if fil.name.strip() == f.name.strip():
                    file.seek(-self.super_block.record_size, 1)
                    file.write(f.get_file_bytes())
                    return True

    def remove_record(self, f, directory):
        """Remove a file record"""
        clusters = self.get_clusters_seq(directory.first_cluster)
        with open('os.txt', 'r+b') as file:
            offset = (clusters.pop(0) - 1) * self.super_block.cluster_size
            file.seek(offset)
            while True:
                if file.tell() == offset + self.super_block.cluster_size:
                    if clusters:
                        offset = (clusters.pop(0) - 1) * self.super_block.cluster_size
                        file.seek(offset)
                    else:
                        return None
                curr_file = File(file_bytes=file.read(self.super_block.record_size))
                if curr_file.full_name == f.full_name:
                    file.seek(-self.super_block.record_size, 1)
                    f.name = ' ' + f.name[1:]
                    file.write(f.get_file_bytes())
                    return True

    def write_data(self, clusters, data):
        """Writes file's data into FS file"""
        with open('os.txt', 'r+b') as file:
            for cluster in clusters[:-1]:
                file.seek((cluster - 1) * self.super_block.cluster_size)
                file.write(data[0:self.super_block.cluster_size])
                data = data[self.super_block.cluster_size:]
            file.seek((clusters[-1] - 1) * self.super_block.cluster_size)
            file.write(data + b' ' * (self.super_block.cluster_size - len(data)))

    def load_users(self):
        """Returns a dict of user's accounts"""
        users = dict()
        rwx, rsh, main_dir = self.get_directory('')
        file = self.read_directory(main_dir).get('users')
        data = self.read_file(file)
        for i in range(1, len(data) // 32 + 1):
            user = User(user_bytes=data[(i-1) * 32:i*32])
            users[user.login.strip()] = user
        return users

    def save_users(self):
        """Save list of users to FS file"""
        data = b''
        for user in self.users.values():
            data += user.get_user_bytes()
        rwx, rsh, main_dir = self.get_directory('')
        file = self.read_directory(main_dir).get('users')
        clusters = self.get_clusters_seq(file.first_cluster)
        data += b' ' * (len(clusters) * self.super_block.cluster_size - len(data))
        self.write_data(clusters, data)

    def path_conversion(self, path):
        """Returns full path to file"""
        if path and path != '/':
            path = self.location + '/' + path if path[0] != '/' else path
        elif path == '/':
            path = ''
        return path

    def get_mod(self, file):
        """Returns file permissions"""
        if file.uid == self.user.id:
            mod = int(file.mod[1:4], 2)
        else:
            mod = int(file.mod[4:], 2)
        return mod

    @staticmethod
    def get_attr(file):
        return int(file.attr, 2)

    @staticmethod
    def parse_file_name(name):
        """Returns name and extension"""
        pos = name.rfind('.')
        ext = ''
        if (-1) < pos < len(name)-1:
            ext = name[pos+1:]
            name = name[:pos]
        if len(name) > 32 or len(ext) > 5:
            raise exeptions.FSExeption('Too long name or extension!')
        return [name, ext]

    def check_dir_r_permission(self, path):
        """Raises exeption if target dir r permission denied else returns target dir"""
        rwx, rsh, directory = self.get_directory(path)
        r, w, x = self.get_binary(rwx)
        if r == '0' and not self.user.role:
            raise exeptions.FSExeption('{}: Permission denied!'.format(self.user.login.strip()))
        return directory

    def check_file_r_permission(self, path, name):
        """Raises exeption if target file/dir r permission denied else returns list with target file and dir"""
        directory = self.check_dir_r_permission(path)
        file = self.read_directory(directory).get(name)
        if not file:
            raise exeptions.FSExeption('{}: File not found!'.format(name))
        rwx = self.get_mod(file)
        r, w, x = self.get_binary(rwx)
        if r == '0' and not self.user.role:
            raise exeptions.FSExeption('{}: Permission denied!'.format(file.full_name))
        return [file, directory]

    def check_dir_w_permission(self, path):
        """Raises exeption if target dir w permission denied else returns target dir"""
        self.check_dir_x_permission(path)
        rwx, rsh, directory = self.get_directory(path)  # reads directories sequence permissions
        r, w, x = self.get_binary(rwx)
        ro, s, h = self.get_binary(rsh)
        if (w == '0' or ro == '1' or s == '1') and not self.user.role:
            raise exeptions.FSExeption('{}: Permission denied!'.format(self.user.login.strip()))
        return directory

    def check_file_w_permission(self, path, name):
        """Raises exeption if target file/dir w permission denied else returns list with target file and dir"""
        directory = self.check_dir_w_permission(path)
        file = self.read_directory(directory).get(name)
        if not file:
            raise exeptions.FSExeption('{}: File not found!'.format(name))
        rwx, rsh = self.get_mod(file), self.get_attr(file)    # check target file permissions
        r, w, x = self.get_binary(rwx)
        ro, s, h = self.get_binary(rsh)
        if (w == '0' or ro == '1' or s == '1') and not self.user.role:
            raise exeptions.FSExeption('{}: Permission denied'.format(self.user.login.strip()))
        return [file, directory]

    def check_dir_x_permission(self, path):
        """Raises exeption if target dir x permission denied else returns target dir"""
        path = self.path_conversion(path)
        rwx, rsh, directory = self.get_directory(path)  # get target directory
        r, w, x = self.get_binary(rwx)
        if x == '0' and not self.user.role:
            raise exeptions.FSExeption('{}: Permission denied!'.format(directory.full_name))
        return directory

    def slice_path(self, path):
        """Returns path to file and file name"""
        full_path = self.path_conversion(path)  # built full path
        last_slash = full_path.rfind('/')   # get pos of last slash
        return [full_path[:last_slash], full_path[last_slash+1:].strip()]    # return path and name

    def get_copy_name(self, target_name, files):
        """Returns new name of copying file"""
        prefix = 1
        name, ext = self.parse_file_name(target_name)
        while files.get('(' + str(prefix) + ')' + target_name):
            prefix += 1
        if len(name) > 32 - len(str(prefix)) - 2:
            raise exeptions.FSExeption('Enter a new name when copying!')
        return '(' + str(prefix) + ')' + target_name

    @staticmethod
    def get_binary(rwx):
        """Returns bin string of int number"""
        string = bin(rwx)[2:]
        if len(string) > 3:
            raise exeptions.FSExeption("Wrong params!")
        string = '0' * (3 - len(string)) + string
        return string
