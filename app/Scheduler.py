import math
import random
from itertools import repeat

from process import Process
from ProcessQueue import ProcessQueue
import exeptions
import time


class Scheduler:
    def __init__(self, user):
        self.user = user
        self.queues = [ProcessQueue(4), ProcessQueue(8), ProcessQueue(16), ProcessQueue(math.inf), ProcessQueue(math.inf)]
        self.removed = list()
        self.curr_queue, self.curr_process = None, None
        self.pid = 1
        self.ticks = 0

    def ps(self):
        string = 'NAME\tUSER\tPID\tNICE\tSTATE\tBURST\tQUEUE'
        for i in range(len(self.queues)):
            for process in self.queues[i]:
                string += '\n' + str(process) + '\t' + str(i)
        return string

    def run(self):
        while True:
            self.curr_queue, self.curr_process = self.get_process()
            if not self.curr_queue and not self.curr_process:
                break
            i = 0
            while i < self.curr_queue.quantum:
                if self.curr_process.state == 'Z':
                    break
                self.quantum_tick()
                i += 1
                time.sleep(1)
                if self.curr_process.cpu_burst == 0:
                    self.kill(self.curr_process.pid)
                    break
                if self.check_displace():
                    break
            else:
                self.move_process_down()

    def nice(self, name, pri, burst):
        if not -20 <= pri <= 19 or burst <= 0:
            raise exeptions.FSExeption('Wrong params!')
        process = Process(name, str(self.user), self.pid, pri, burst)
        process.history = '-' * self.ticks
        self.pid += 1
        if self.user.role:
            self.queues[0].append(process)
        else:
            self.queues[1].append(process)

    def renice(self, pid, pri):
        if not -20 <= pri <= 19:
            raise exeptions.FSExeption('Wrong params!')
        process, queue = self.find(pid)
        self.check_permissions(process, queue)
        process.priority = pri

    def kill(self, pid):
        process, queue = self.find(pid)
        self.check_permissions(process, queue)
        if process == self.curr_process:
            self.curr_process.state = 'Z'
        queue.remove(process)
        self.removed.append(process)

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
        self.curr_process.state = 'W'
        self.curr_process.wait_cpu_burst = random.randint(1, 5)
        self.curr_queue.remove(self.curr_process)
        self.queues[-1].append(self.curr_process)

    def move_process_down(self):
        index = self.queues.index(self.curr_queue) + 1
        self.curr_queue.remove(self.curr_process)
        self.queues[index].append(self.curr_process)
        self.curr_process.state = 'R'

    def check_permissions(self, process, queue):
        if not process or not queue:
            raise exeptions.FSExeption('Process not found!')
        if process.user != str(self.user) and not self.user.role:
            raise exeptions.FSExeption('{}: Permission denied!'.format(self.user))

    def quantum_tick(self):
        for queue in self.queues:
            queue = list(map(self.update_processes, queue))
        self.ticks += 1

    def get_process(self):
        for queue in self.queues:
            for process in queue:
                process.state = 'E' if process.state != 'W' else 'W'
                return [queue, process]
        return [None, None]

    @staticmethod
    def update_processes(process):
        if process.state == 'E':
            process.cpu_burst -= 1
        process.history += process.state
