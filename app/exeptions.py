class FSExeption(Exception):
    def __init__(self, message):
        self.txt = message

    def __str__(self):
        return self.txt
