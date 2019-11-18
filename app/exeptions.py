class FileExists(Exception):
    def __init__(self, filename):
        self.txt = 'File with name "' + filename + '" is already exist!'

    def __str__(self):
        return self.txt


class FileNotExists(Exception):
    def __init__(self):
        self.txt = 'No such file or directory!'

    def __str__(self):
        return self.txt


class IncorrectLoginOrPass(Exception):
    def __init__(self):
        self.text = 'Incorrect login or password!'

    def __str__(self):
        return self.text


class NotEnoughParams(Exception):
    def __init__(self):
        self.txt = 'Not enough params!'

    def __str__(self):
        return self.txt


class PermissionsDenied(Exception):
    def __init__(self):
        self.txt = 'Permissions denied!'

    def __str__(self):
        return self.txt
