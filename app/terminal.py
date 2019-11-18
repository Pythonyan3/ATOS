import hashlib
import os
import atos
import exeptions
from formatting import Formatting
from termcolor import colored


class Terminal:

    def __init__(self, path):

        if os.path.isfile(path):
            # self.formatting()
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
                except exeptions.IncorrectLoginOrPass as e:
                    print(colored(e, 'red'))

    def authorization(self):
        login = self.get_string(colored('Enter your login: ', 'white'))
        password = self.get_string(colored('Enter your password: ', 'white'))
        return self.atos.login(login, password)

    def logout(self, params):
        self.atos.logout()

    def commands(self, command):
        return {
            'mkfile': self.mkfile,
            'mkdir': self.mkdir,
            'mkuser': self.mkuser,
            'rmuser': self.rmuser,
            'ls': self.ls,
            'pwd': self.pwd,
            'cd': self.cd,
            'logout': self.logout,
            'clear': self.clear
        }.get(command)

    def mkfile(self, params):
        if self.check_file_name(params):
            for param in params:
                try:
                    self.atos.make_file(param)
                except exeptions.FileExists as e:
                    print(colored(e, 'red'))
                except exeptions.FileNotExists as e:
                    print(colored(e, 'red'))

    def mkdir(self, params):
        if self.check_file_name(params):
            for param in params:
                try:
                    self.atos.make_file(path=param, mod='1111101')
                except exeptions.FileExists as e:
                    print(colored(e, 'red'))
                except exeptions.FileNotExists as e:
                    print(colored(e, 'red'))

    def mkuser(self, params):
        self.atos.make_user(params)

    def rmuser(self, params):
        if len(params) == 1:
            self.atos.remove_user(params[0])

    def ls(self, params):
        x, files = self.atos.show_dir(params[0]) if params else self.atos.show_dir(self.atos.location)
        for file in files.values():
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
        except exeptions.FileNotExists as e:
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

    def make_users(self):
        data = b'root' + b' ' * 10 + hashlib.md5(b'314ton').digest() + (1).to_bytes(1, byteorder='big') + \
               (1).to_bytes(1, byteorder='big')
        self.atos.make_file(path='users', attr='111', data=data)

    def formatting(self):
        form = Formatting()
        form.formatting()

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
