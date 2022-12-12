class QMI:

    def __init__(self, tasks, allocs, num_reads, anneal_time=20):
        self.tasks = tasks
        self.allocs = allocs
        self.num_reads = num_reads
        self.anneal_time = anneal_time
        
        self.time_start = None
        self.time_end = None
        self.time_program = None
        self.time_sample = None


    def getTasks(self):
        return self.tasks.copy()


    def getAllocs(self):
        return self.allocs.copy()
    
    
    def getDeviceCapacity(self):
        cols, rows = self.allocs[0].shape
        return cols * rows 


    def setNumReads(self, num_reads):
        self.num_reads = num_reads


    def getNumReads(self):
        return self.num_reads


    def getAnnealTime(self):
        return self.anneal_time
    
    
    def stampTime(self, t_start, t_end, t_prog, t_sample):
        self.time_start = t_start
        self.time_end = t_end
        self.time_program = t_prog
        self.time_sample = t_sample


    def getTiming(self):
        return self.time_start, self.time_end, self.time_program, self.time_sample


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
