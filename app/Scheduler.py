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
        """Returns a list of processes states"""
        result = [''.join(map(lambda s: s.ljust(10), ('NAME', 'USER', 'PID', 'NICE', 'STATE', 'BURST', 'QUEUE')))]
        for queue in self.queues:
            for process in queue:
                result.append(str(process))
        result.append('\n')
        return result

    def run(self, delay):
        """Processes planning"""
        while True:
            self.trace.extend(self.ps())
            self.curr_queue, self.curr_process = self.__get_process()
            if not self.curr_queue and not self.curr_process or self.pause:
                break
            self.curr_process.state = 'E' if self.curr_process.state == 'R' else 'W'
            i = 0
            while i < self.curr_queue.quantum:
                if self.pause or self.curr_process.state == 'Z':
                    break
                time.sleep(delay)
                self.__tact()
                i += 1
                if self.curr_process.cpu_burst == 0:
                    self.kill(self.curr_process.pid, True)
                    break
                if self.curr_process.state == 'W' or self.curr_process.state == 'R':
                    break
                if self.curr_process.state == 'E' and self.__generate_waiting() or self.__check_displace():
                    break
            else:
                self.__move_process_down()

    def nice(self, name, pri, burst):
        """Make a new process"""
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
        """Changes process NICE"""
        if not -20 <= pri <= 19:
            raise exeptions.FSExeption('Wrong params!')
        if pri < 0 and not self.user.role:
            raise exeptions.FSExeption('{}: Permission denied!'.format(self.user))
        process, queue = self.__find(pid)
        self.__check_permissions(process, queue)
        process.pri = pri
        queue.remove(process)
        queue.__append(process)

    def kill(self, pid, su=False):
        """Kills a process"""
        process, queue = self.__find(pid)
        if not su:
            self.__check_permissions(process, queue)
        process.state = 'Z'
        queue.remove(process)
        self.finished_processes.append(process)

    def __find(self, pid):
        """Returns process and queue by a PID"""
        process, queue = None, None
        for queue in self.queues:
            for process in queue:
                if process.pid == pid:
                    return [process, queue]
        return [process, queue]

    def __check_displace(self):
        """Checks a new more priority process"""
        queue, process = self.__get_process()
        if process != self.curr_process:
            self.curr_process.state = 'R'
            return True

    def __generate_waiting(self):
        """Randomize waiting state"""
        if 1 <= random.randint(1, 100) <= 5:
            self.curr_process.state = 'W'
            self.curr_process.wait_cpu_burst = random.randint(1, 5)
            self.curr_queue.remove(self.curr_process)
            self.queues[-1].append(self.curr_process)
            return True

    def __move_process_down(self):
        """Moves process to less priority queue"""
        self.curr_queue.remove(self.curr_process)
        self.queues[self.curr_queue.number+1].append(self.curr_process)
        self.curr_process.state = 'R'

    def __move_process_up(self, process):
        """Moves process to more priority queue"""
        process.state = 'R'
        self.queues[-1].remove(process)
        if process.user.role:
            self.queues[0].append(process)
        else:
            self.queues[1].append(process)

    def __check_permissions(self, process, queue):
        """Checks user permissions"""
        if not process or not queue:
            raise exeptions.FSExeption('Process not found!')
        if str(process.user) != str(self.user) and not self.user.role:
            raise exeptions.FSExeption('{}: Permission denied!'.format(self.user))

    def __tact(self):
        """Does one tact. Change cpu_burst field of curr_process and waiting processes"""
        self.curr_process.cpu_burst -= 1
        for process in self.queues[-1]:
            process.wait_cpu_burst -= 1
            if process.wait_cpu_burst == 0:
                self.__move_process_up(process)

    def __get_process(self):
        """Returns process to executing"""
        for queue in self.queues:
            for process in queue:
                return [queue, process]
        return [None, None]

    def tracing(self):
        """Returns tracing"""
        return self.trace
