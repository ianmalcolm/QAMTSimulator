class QMI:

    def __init__(self, tasks, allocs, num_reads, anneal_time=20):
        self.tasks = tasks
        self.allocs = allocs
        self.num_reads = num_reads
        self.anneal_time = anneal_time


    def getTasks(self):
        return self.tasks.copy()


    def getAllocs(self):
        return self.allocs.copy()


    def setNumReads(self, num_reads):
        self.num_reads = num_reads


    def getNumReads(self):
        return self.num_reads


    def getAnnealTime(self):
        return self.anneal_time


    def fromTask(task):
        return QMI(
            tasks=[task],
            allocs=[task.getEmbd()],
            num_reads=task.getNumReads(),
            anneal_time=task.getAnnealTime(),
        )


    def fromSched(tasks):
        ts, allocs, durs = zip(*tasks)
        return QMI(
            tasks=list(ts),
            allocs=list(allocs),
            num_reads=max(durs),
            anneal_time=ts[0].getAnnealTime(),
        )
