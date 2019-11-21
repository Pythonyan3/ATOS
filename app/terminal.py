import hashlib
import getpass
import os
import atos
import exeptions
from formatting import Formatting
from termcolor import colored


class Terminal:

    def __init__(self, path):

        if os.path.isfile(path):
            self.atos = atos.Atos(path)
            # self.make_users()

    def run(self):
        while True:
            if self.atos.user:
                print(colored(self.atos.user, 'green') + colored('~' + self.atos.location, 'blue') + ": ", end='')
                string = input()
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

    def authorization(self):
        login = self.get_string(colored('Enter your login: ', 'white'))
        password = getpass.getpass('Enter your password: ')
        return self.atos.login(login, password)

    def logout(self, params):
        self.atos.logout()

    def commands(self, command):
        return {
            'mkfile': self.mkfile,
            'mkdir': self.mkdir,
            'rm': self.rm,
            'mv': self.mv,
            'mkuser': self.mkuser,
            'rmuser': self.rmuser,
            'chmod': self.chmod,
            'chattr': self.chattr,
            'open': self.open,
            'ls': self.ls,
            'pwd': self.pwd,
            'cd': self.cd,
            'logout': self.logout,
            'fsform': self.formatting,
            'clear': self.clear
        }.get(command)

    def mkfile(self, params):
        if self.check_file_name(params):
            for param in params:
                try:
                    self.atos.make_file(param)
                except exeptions.FSExeption as e:
                    print(colored(e, 'red'))

    def mkdir(self, params):
        if self.check_file_name(params):
            for param in params:
                try:
                    self.atos.make_file(path=param, mod='1111101')
                except exeptions.FSExeption as e:
                    print(colored(e, 'red'))

    def rm(self, params):
        if len(params) == 1:
            try:
                self.atos.remove_file(params[0])
            except exeptions.FSExeption as e:
                print(colored(e, 'red'))
        else:
            print(colored('Wrong params!', 'red'))

    def mv(self, params):
        if len(params) == 2:
            try:
                self.atos.move_file(params[0], params[1])
            except exeptions.FSExeption as e:
                print(colored(e, 'red'))
        else:
            print(colored('Wrong params!', 'red'))

    def mkuser(self, params):
        try:
            self.atos.make_user(params)
        except exeptions.FSExeption as e:
            print(colored(e, 'red'))

    def rmuser(self, params):
        if len(params) == 1:
            try:
                self.atos.remove_user(params[0])
            except exeptions.FSExeption as e:
                print(colored(e, 'red'))

    def chmod(self, params):
        if len(params) == 2:
            self.atos.change_mod(params[1], params[0])

    def chattr(self, params):
        if len(params) == 2:
            self.atos.change_attr(params[1], params[0])
        else:
            print(colored('Not enough params!', 'red'))

    def open(self, params):
        if params:
            try:
                print(self.atos.open(params[0]))
            except exeptions.FSExeption as e:
                print(colored(e, 'red'))

    def ls(self, params):
        x, files = self.atos.show_dir(params[0]) if params else self.atos.show_dir(self.atos.location)
        for file in files.values():
            if file.attr[2] == '1' and not self.atos.user.role:
                continue
            if file.mod[0] == '1':
                string = file if x == '1' else file.full_name
                print(colored(string, 'magenta'))
            else:
                string = file if x == '1' else file.full_name
                print(string)

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
    def formatting(self):
        formatter = Formatting()
        formatter.formatting()

    @staticmethod
    def check_file_name(names):
        if names:
            for name in names:
                if name.find('//') != -1:
                    print(colored(name + ': Wrong name', 'red'))    # if name contains '//'
                    return False
                elif not 0 < len(name.split('/')[-1]) <= 20:    # if len not between 1-20
                    print(colored(name + ': Wrong name', 'red'))
                    return False
            return True
        print(colored('Not enough params', 'red'))
