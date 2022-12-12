import numpy as np

class Chimera:

    def __init__(self, resources=None):

        if resources is None:
            self.res = np.zeros((16, 16), dtype=int)
        elif isinstance(resources, (list, tuple)) and len(resources) == 2:
            self.res = np.zeros(resources, dtype=int)
        else:
            self.res = resources

        self.last_inst = None


    def getRes(self):
        return self.res.copy()


    def getProgramTime(self, inst):
        return 1000


    def getLastInst(self):
        return self.last_inst


    def execute(self, inst, t):

        num_reads = inst.getNumReads()

        t_prog = self.getProgramTime(inst)
        t_neal = inst.getAnnealTime()
        t_samp = t_neal * num_reads
        t_exec = t_prog + t_samp

        for task in inst.getTasks():
            if t_prog > 0:
                task.log( 'program', (t, t+t_prog),               1)
                task.log(  'sample', (t+t_prog, t+t_prog+t_neal), num_reads)
            else:
                task.log(  'sample', (t, t+t_neal),               num_reads)
            task.samplePlusOne(num_reads)

        inst.time_start = t
        inst.time_end = t + t_exec
        inst.time_program = t_prog
        inst.time_sample = t_samp

        self.last_inst = inst

        return t + t_exec
