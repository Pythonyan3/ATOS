class ProcessQueue(list):
    def __init__(self, quantum=5):
        super().__init__()
        self.quantum = quantum

    def append(self, obj):
        if not self:
            super().append(obj)
        else:
            for i in range(len(self)):
                if self[i].pri > obj.pri:
                    self.insert(i, obj)
