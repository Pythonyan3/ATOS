class ProcessQueue(list):
    def __init__(self, number, quantum):
        super().__init__()
        self.number = number
        self.quantum = quantum

    def append(self, process):
        process.qid = self.number
        for i in range(len(self)):
            if self[i].pri > process.pri:
                self.insert(i, process)
                return None
        super().append(process)
