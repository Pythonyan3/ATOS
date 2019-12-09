import math
import random
from process import Process
from ProcessQueue import ProcessQueue
import exeptions
import time


class Scheduler:
    def __init__(self, user):
        self.user = user
        self.queues = [ProcessQueue(0, 4), ProcessQueue(1, 8), ProcessQueue(2, 16),
                       ProcessQueue(3, math.inf), ProcessQueue(4, math.inf)]
        self.finished_processes = list()
        self.curr_queue, self.curr_process = None, None
        self.pid = 1
        self.pause = False
        self.trace = list()

    def ps(self):
        result = [''.join(map(lambda s: s.ljust(10), ('NAME', 'USER', 'PID', 'NICE', 'STATE', 'BURST', 'QUEUE')))]
        for queue in self.queues:
            for process in queue:
                result.append(str(process))
        result.append('\n')
        return result

    def run(self, delay):
        while True:
            self.trace.extend(self.ps())
            self.curr_queue, self.curr_process = self.get_process()
            if not self.curr_queue and not self.curr_process or self.pause:
                break
            self.curr_process.state = 'E' if self.curr_process.state == 'R' else 'W'
            i = 0
            while i < self.curr_queue.quantum:
                if self.pause or self.curr_process.state == 'Z':
                    break
                time.sleep(delay)
                self.tact()
                i += 1
                if self.curr_process.cpu_burst == 0:
                    self.kill(self.curr_process.pid, True)
                    break
                if self.curr_process.state == 'W' or self.curr_process.state == 'R':
                    break
                if self.curr_process.state == 'E' and self.generate_waiting() or self.check_displace():
                    break
            else:
                self.move_process_down()

    def nice(self, name, pri, burst):
        if not -20 <= pri <= 19 or burst <= 0:
            raise exeptions.FSExeption('Wrong params!')
        if pri < 0 and not self.user.role:
            raise exeptions.FSExeption('{}: Permission denied!'.format(self.user))
        process = Process(name, self.user, self.pid, pri, burst)
        if self.user.role:
            self.queues[0].append(process)
        else:
            self.queues[1].append(process)
        self.pid += 1

    def renice(self, pid, pri):
        if not -20 <= pri <= 19:
            raise exeptions.FSExeption('Wrong params!')
        if pri < 0 and not self.user.role:
            raise exeptions.FSExeption('{}: Permission denied!'.format(self.user))
        process, queue = self.find(pid)
        self.check_permissions(process, queue)
        process.pri = pri
        queue.remove(process)
        queue.append(process)

    def kill(self, pid, su=False):
        process, queue = self.find(pid)
        if not su:
            self.check_permissions(process, queue)
        process.state = 'Z'
        queue.remove(process)
        self.finished_processes.append(process)

    def find(self, pid):
        process, queue = None, None
        for queue in self.queues:
            for process in queue:
                if process.pid == pid:
                    return [process, queue]
        return [process, queue]

    def check_displace(self):
        queue, process = self.get_process()
        if process != self.curr_process:
            self.curr_process.state = 'R'
            return True

    def generate_waiting(self):
        if 1 <= random.randint(1, 100) <= 5:
            self.curr_process.state = 'W'
            self.curr_process.wait_cpu_burst = random.randint(1, 5)
            self.curr_queue.remove(self.curr_process)
            self.queues[-1].append(self.curr_process)
            return True

    def move_process_down(self):
        self.curr_queue.remove(self.curr_process)
        self.queues[self.curr_queue.number+1].append(self.curr_process)
        self.curr_process.state = 'R'

    def move_process_up(self, process):
        process.state = 'R'
        self.queues[-1].remove(process)
        if process.user.role:
            self.queues[0].append(process)
        else:
            self.queues[1].append(process)

    def check_permissions(self, process, queue):
        if not process or not queue:
            raise exeptions.FSExeption('Process not found!')
        if str(process.user) != str(self.user) and not self.user.role:
            raise exeptions.FSExeption('{}: Permission denied!'.format(self.user))

    def tact(self):
        for queue in self.queues:
            for process in queue:
                if process.state == 'E':
                    process.cpu_burst -= 1
                if process.state == 'W':
                    process.wait_cpu_burst -= 1
                    if process.wait_cpu_burst == 0:
                        self.move_process_up(process)

    def get_process(self):
        for queue in self.queues:
            for process in queue:
                return [queue, process]
        return [None, None]

    def tracing(self):
        return self.trace
