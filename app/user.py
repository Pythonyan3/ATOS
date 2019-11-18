class User:
    def __init__(self, file_bytes):
        self.login = str(file_bytes[:14], 'ansi')
        self.password = file_bytes[14:30]
        self.id = int.from_bytes(file_bytes[30:31], byteorder='big')
        self.role = int.from_bytes(file_bytes[31:32], byteorder='big')

    def __str__(self):
        return self.login.strip()
