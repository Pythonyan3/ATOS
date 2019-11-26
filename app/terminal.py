import hashlib
import getpass
import os
import atos
import exeptions
from file import File
from termcolor import colored


class Terminal:

    def __init__(self, path):
        self.atos = atos.Atos(path)

    def run(self):
        while True:
            if self.atos.user:
                label = colored(self.atos.user, 'green') + colored('~' + self.atos.location, 'blue') + ": "
                string = self.get_string(label)
                if string:
                    user_command = string.split(' ')
                    command = user_command.pop(0)
                    function = self.commands(command)
                    if function:
                        function(list(filter(None, user_command)))
                    else:
                        print(colored('Unknown command!', 'red'))
            else:
                try:
                    self.authorization()
                except exeptions.FSExeption as e:
                    print(colored(e, 'red'))

    def commands(self, command):
        return {
            'mkfile': self.mkfile,
            'mkdir': self.mkdir,
            'rm': self.rm,
            'mv': self.mv,
            'cp': self.cp,
            'mkuser': self.mkuser,
            'rmuser': self.rmuser,
            'chmod': self.chmod,
            'chattr': self.chattr,
            'open': self.open,
            'write': self.write,
            'append': self.append,
            'ls': self.ls,
            'pwd': self.pwd,
            'cd': self.cd,
            'logout': self.logout,
            'fsformat': self.formatting,
            'clear': self.clear,
            'help': self.help
        }.get(command)

    def mkfile(self, params):
        if not params:
            print(colored('Not enough params!', 'red'))
        for param in params:
            try:
                self.atos.make_file(param)
            except exeptions.FSExeption as e:
                print(colored(e, 'red'))

    def mkdir(self, params):
        if not params:
            print(colored('Not enough params!', 'red'))
        for param in params:
            try:
                self.atos.make_file(path=param, mod='1111101')
            except exeptions.FSExeption as e:
                print(colored(e, 'red'))

    def rm(self, params):
        if not params:
            print(colored('Not enough params!', 'red'))
        for param in params:
            try:
                self.atos.remove_file(param)
            except exeptions.FSExeption as e:
                print(colored(e, 'red'))

    def mv(self, params):
        if len(params) == 2:
            try:
                self.atos.move_file(params[0], params[1])
            except exeptions.FSExeption as e:
                print(colored(e, 'red'))
        else:
            print(colored('Wrong params!', 'red'))

    def cp(self, params):
        if params:
            try:
                if len(params) == 2:
                    self.atos.copy_file(params[0], params[1])
                elif len(params) == 1:
                    self.atos.copy_file(params[0], params[0])
            except exeptions.FSExeption as e:
                print(colored(e, 'red'))
        else:
            print(colored('Wrong params!', 'red'))

    def mkuser(self, params):
        if len(params) == 3 and params[2].isdigit():
            try:
                self.atos.make_user(params)
            except exeptions.FSExeption as e:
                print(colored(e, 'red'))
        else:
            print(colored('Wrong params!'))

    def rmuser(self, params):
        if len(params) == 1:
            try:
                self.atos.remove_user(params[0])
            except exeptions.FSExeption as e:
                print(colored(e, 'red'))

    def chmod(self, params):
        if len(params) == 2:
            try:
                self.atos.change_mod(params[1], params[0])
            except exeptions.FSExeption as e:
                print(colored(e, 'red'))
        else:
            print(colored('Wrong params!', 'red'))

    def chattr(self, params):
        if len(params) == 2 and params[0].isdigit():
            try:
                self.atos.change_attr(params[1], params[0])
            except exeptions.FSExeption as e:
                print(colored(e, 'red'))
        else:
            print(colored('Wrong params!', 'red'))

    def open(self, params):
        if params:
            try:
                data = self.atos.open(params[0])
                if data:
                    print(data)
            except exeptions.FSExeption as e:
                print(colored(e, 'red'))
        else:
            print(colored('Not enough params!', 'red'))

    def write(self, params):
        try:
            self.atos.write_permission(params[0])
            data = self.get_strings()
            self.atos.write(params[0], data)
        except exeptions.FSExeption as e:
            print(colored(e, 'red'))

    def append(self, params):
        try:
            self.atos.write_permission(params[0])
            data = self.get_strings()
            self.atos.append(params[0], data)
        except exeptions.FSExeption as e:
            print(colored(e, 'red'))

    def ls(self, params):
        try:
            files = self.atos.show_dir(params[0]) if params else self.atos.show_dir(self.atos.location)
            for file in files:
                if type(file) == File:
                    color = 'magenta' if file.mod[0] == '1' else 'white'
                    print(colored(file, color))
                else:
                    print(file)
        except exeptions.FSExeption as e:
            print(colored(e, 'red'))

    def pwd(self, params):
        path = self.atos.location
        path = path if path else '/'
        print(path)

    def cd(self, params):
        try:
            if params and len(params) == 1:
                self.atos.change_directory(params[0])
            else:
                print(colored('Wrong params!', 'red'))
        except exeptions.FSExeption as e:
            print(colored(e, 'red'))

    def authorization(self):
        login = self.get_string(colored('Enter your login: ', 'white'))
        password = getpass.getpass('Enter your password: ')
        return self.atos.login(login, password)

    def logout(self, params):
        self.atos.logout()

    @staticmethod
    def clear(params):
        os.system('cls')

    @staticmethod
    def get_string(label):
        while True:
            print(label, end='')
            text = input()
            if text.strip():
                return text.strip()

    @staticmethod
    def get_strings():
        strings = list()
        while True:
            try:
                strings.append(input())
            except EOFError:
                break
        return '\n'.join(strings)

    def formatting(self, params):
        try:
            if params:
                if len(params) == 2 and params[0].isdigit() and params[1].isdigit():
                    self.atos.fs_formatting(int(params[0]), int(params[1]))
                else:
                    print(colored('Wrong params', 'red'))
            else:
                self.atos.fs_formatting()
            print('Formatting done.')
        except exeptions.FSExeption as e:
            print(colored(e, 'red'))

    def help(self, params):
        string = 'mkfile    [file name*]\n' \
                 'mkdir     [directory name*]\n' \
                 'rm        [file/directory name*]\n' \
                 'mv        [source file name*, destination file name*]\n' \
                 'cp        [source file name*, destination file name]\n' \
                 'chmod     [owner permissions(0-7)|other permissions(0-7)*, file name*]\n' \
                 'chattr    [file attributes(readonly, system, hidden)(0-7)*, file name*]\n' \
                 'open      [file name*]\n' \
                 'write     [file name*]\n' \
                 'ls        [path]\n' \
                 'pwd       []\n' \
                 'cd        [path*]\n' \
                 'mkuser    [login*, password*, role (0-1)*]\n' \
                 'rmuser    [login*]\n' \
                 'logout    []\n' \
                 'fsformat  [HD size (20-1024), cluster size (512-32768)]\n' \
                 'clear     []'
        print(string)
