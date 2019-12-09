class Process:
    def __init__(self, name, user, pid, pri, burst, qid=0):
        self.name = name
        self.user = user
        self.pid = pid
        self.qid = qid
        self.state = 'R'
        self.cpu_burst = burst
        self.wait_cpu_burst = 0
        self.pri = pri

    def __str__(self):
        burst = str(self.cpu_burst) if self.state != 'W' else str(self.wait_cpu_burst)
        fields = (self.name, str(self.user), str(self.pid), str(self.pri), self.state, burst, str(self.qid))
        fields = [f.ljust(10) for f in fields]
        return ''.join(fields)
