import json
import random
import numpy as np

class Task:

    def __init__(self, embd=None, name=None, t_arrive=0, num_reads=100, anneal_time=20, anneal_schedule=None, **kwargs):
        
        self.embd = embd
        self.name = name or f'{random.randrange(0xffffffff)}'
        self.num_reads = num_reads
        self.anneal_time = anneal_time
        self.anneal_schedule = anneal_schedule
        
        self.t_arrive = t_arrive
        self.samples_complete = 0
        self.activity_logs = []


    def __repr__(self):
        return self.name


    def log(self, name, period, repeat):
        self.activity_logs.append((name, period, repeat))


    def getLogs(self):
        return self.activity_logs.copy()


    def getNumReads(self):
        pass


    def getAnnealTime(self):
        return self.anneal_time


    def getEmbd(self):
        return self.embd


    def getReq(self):
        return self, self.embd, self.getSampleRemain()


    def getTimeArrive(self):
        return self.t_arrive


    def samplePlusOne(self, s=1):
        remain = self.getSampleRemain()
        self.samples_complete += s
        if remain > s:
            return None
        else:
            return remain


    def isComplete(self):
        return self.getSampleRemain() == 0


    def getSampleRemain(self):
        return max(0, self.num_reads - self.samples_complete)


    @staticmethod
    def load(data):
        
        for t in data:
            try:
                embd = eval(t['embd'])
            except SyntaxError:
                loc={}
                exec(t['embd'], globals(), loc)
                if 'embd' not in loc:
                    raise ValueError(f'Invalid embedding for task {t}')
                embd = loc['embd']
            t['embd'] = embd
        if isinstance(data, list):
            return [Task(**d) for d in data]
        else:
            return Task(**data)

        
