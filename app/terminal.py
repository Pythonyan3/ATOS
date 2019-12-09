import getpass
import os
import threading
import time
import atos
import exeptions
from file import File
from termcolor import colored
from colorama import Fore, Back
from Scheduler import Scheduler


class Terminal:

    def __init__(self, path):
        self.atos = atos.Atos(path)
        self.scheduler = Scheduler(self.atos.user)
        self.thread = threading.Thread(target=self.scheduler.run, daemon=True)

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
            'users': self.users,
            'chmod': self.chmod,
            'chattr': self.chattr,
            'open': self.open,
            'write': self.write,
            'append': self.append,
            'ls': self.ls,
            'pwd': self.pwd,
            'cd': self.cd,
            'logout': self.logout,
            'nice': self.nice,
            'renice': self.renice,
            'kill': self.kill,
            'ps': self.ps,
            'top': self.top,
            'planning': self.scheduler_run,
            'plpause': self.scheduler_pause,
            'trace': self.trace,
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
                self.atos.make_user(params[0], params[1], params[2])
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

    def users(self, params):
        for user in self.atos.users_list():
            role = 'superuser' if user.role else 'user'
            print(str(user) + '\t' + role)

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
            files = self.atos.show_directory(params[0]) if params else self.atos.show_directory(self.atos.location)
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
        self.atos.login(login, password)
        self.scheduler.user = self.atos.user

    def logout(self, params):
        self.atos.logout()

    def nice(self, params):
        try:
            self.scheduler.nice(params[0], int(params[1]), int(params[2]))
        except ValueError:
            print(colored('Wrong params!', 'red'))
        except IndexError:
            print(colored('Wrong params!', 'red'))
        except exeptions.FSExeption as e:
            print(colored(e, 'red'))

    def renice(self, params):
        try:
            self.scheduler.renice(int(params[0]), int(params[1]))
        except ValueError:
            print(colored('Wrong params!', 'red'))
        except IndexError:
            print(colored('Wrong params!', 'red'))
        except exeptions.FSExeption as e:
            print(colored(e, 'red'))

    def kill(self, params):
        try:
            self.scheduler.kill(int(params[0]))
        except ValueError:
            print(colored('Wrong params!', 'red'))
        except IndexError:
            print(colored('Wrong params!', 'red'))
        except exeptions.FSExeption as e:
            print(colored(e, 'red'))

    def ps(self, params):
        process_list = self.scheduler.ps()
        process_list[0] = Fore.BLACK + Back.WHITE + process_list[0] + Fore.RESET + Back.RESET
        for s in process_list:
            print(str(s))

    def top(self, params):
        if params and len(params) == 1 and params[0].isdigit() and int(params[0]) >= 0:
            duration = int(params[0])
        else:
            duration = 5
        while True:
            try:
                self.clear(params)
                process_list = self.scheduler.ps()
                process_list[0] = Fore.BLACK + Back.WHITE + process_list[0] + Fore.RESET + Back.RESET
                for s in process_list:
                    print(str(s))
                time.sleep(duration)
            except KeyboardInterrupt:
                self.clear(params)
                break

    def scheduler_run(self, params):
        if not self.thread.is_alive():
            delay = 1 if (len(params) != 1 or not params[0].isdigit()) else float(params[0])
            self.scheduler.pause = False
            self.thread = threading.Thread(target=self.scheduler.run, args=(delay,), daemon=True)
            self.thread.start()
        else:
            print(colored('Scheduler is already running!', 'red'))

    def scheduler_pause(self, params):
        self.scheduler.pause = True

    def trace(self, params):
        with open('trace.txt', 'w') as file:
            for string in self.scheduler.tracing():
                file.write(str(string) + '\n')

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
        string = 'mkfile    make a new file     [file name*]\n' \
                 'mkdir     make a new dir      [directory name*]\n' \
                 'rm        remove file/dir     [file/directory name*]\n' \
                 'mv        move file/dir       [source file name*, destination file name*]\n' \
                 'cp        copy file/dir       [source file name*, destination file name]\n' \
                 'chmod     change mode         [owner permissions(0-7)|other permissions(0-7)*, file name*]\n' \
                 'chattr    change attributes   [file attributes(readonly, system, hidden)(0-7)*, file name*]\n' \
                 'open      read file           [file name*]\n' \
                 'append    append data         [file name*]\n' \
                 'write     write data          [file name*]\n' \
                 'ls        show dir            [path]\n' \
                 'pwd       show location       []\n' \
                 'cd        change location     [path*]\n' \
                 'mkuser    make new user       [login*, password*, role (0-1)*]\n' \
                 'rmuser    remove user         [login*]\n' \
                 'users     list of users       []\n' \
                 'logout    logout              []\n' \
                 'nice      create process      [name*, nice*, cpu burst*]\n' \
                 'renice    change process pri  [PID*, nice*]\n' \
                 'kill      kill process        [PID*]\n' \
                 'ps        processes list      []\n' \
                 'top       processes list      [delay]\n' \
                 'planning  start planning      [delay]\n' \
                 'plpause   pause planning      []\n' \
                 'trace     write tracing       []\n' \
                 'fsformat  format FS           [HD size (20-1024), cluster size (512-32768)]\n' \
                 'clear     clear terminal      []'
        print(string)
