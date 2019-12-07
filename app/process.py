class Process:
    def __init__(self, name, user_name, pid, pri, burst):
        self.name = name
        self.user = user_name
        self.pid = pid
        self.state = 'R'
        self.cpu_burst = burst
        self.wait_cpu_burst = 0
        self.pri = pri
        self.history = ''

    def __str__(self):
        string = self.name + '\t' + self.user + '\t' + str(self.pid) + '\t' + \
                 str(self.pri) + '\t' + self.state
        if self.state == 'W':
            string += '\t' + str(self.wait_cpu_burst)
        else:
            string += '\t' + str(self.cpu_burst)
        return string

    def is_waiting(self):
        return not self.state
