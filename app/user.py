class User:
    def __init__(self, user_bytes='', login='', password=b'', id=0, role=0):
        if user_bytes:
            self.parse_bytes(user_bytes)
        else:
            self.login = login + ' ' * (14 - len(login))
            self.password = password
            self.id = id
            self.role = role

    def __str__(self):
        return self.login.strip()

    def parse_bytes(self, user_bytes):
        self.login = str(user_bytes[:14], 'ansi')
        self.password = user_bytes[14:30]
        self.id = int.from_bytes(user_bytes[30:31], byteorder='big')
        self.role = int.from_bytes(user_bytes[31:32], byteorder='big')

    def get_user_bytes(self):
        b = bytes(self.login, 'ansi')
        b += self.password + self.id.to_bytes(1, byteorder='big') + self.role.to_bytes(1, byteorder='big')
        return b
