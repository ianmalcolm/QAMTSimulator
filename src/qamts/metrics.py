import numpy as np
import time


class TaskTiming:

    def __init__(self, tasks):
        self.tasks = tasks

    def getTiming(self):
        return [(t, t.getTimeArrive(), t.getLogStartTime(), t.getLogEndTime()) for t in self.tasks]

    def ACET(self):
        return np.mean([t.getLogEndTime() - t.getLogStartTime() for t in self.tasks])

    def WCET(self):
        return np.max([t.getLogEndTime() - t.getLogStartTime() for t in self.tasks])

    def ACRT(self):
        return np.mean([t.getLogEndTime() - t.getTimeArrive() for t in self.tasks])

    def WCRT(self):
        return np.max([t.getLogEndTime() - t.getTimeArrive() for t in self.tasks])

    def ACIWT(self):
        return np.mean([t.getLogStartTime() - t.getTimeArrive() for t in self.tasks])

    def WCIWT(self):
        return np.max([t.getLogStartTime() - t.getTimeArrive() for t in self.tasks])


def calcResourceUtilisation(insts):
    tasks = []
    for inst in insts:
        tasks.extend(inst.getTasks())
    tasks = list(set(tasks))
    total_reqs = sum([t.getEmbd().sum() * t.getNumSamples() * t.getAnnealTime() for t in tasks])
    period = max([inst.getTiming()[1] for inst in insts]) - min([inst.getTiming()[0] for inst in insts])
    total_res = insts[0].getDeviceCapacity() * period
    return total_reqs / total_res


class SchedulerSpeedometer:

    def __init__(self):
        self.logs = []

    def decorate(self, func):

        def wrapper(tasks, annealer):
            t_start = time.time()
            ret = func(tasks, annealer)
            t_end = time.time()
            log = t_end - t_start, tasks.copy(), annealer
            self.logs.append(log)
            return ret
    
        return wrapper

    def getStats(self):
        stats = []
        for period, tasks, annealer in self.logs:
            t_sizes = [t.getEmbd().size / annealer.getRes().size for t in tasks]
            stats.append((tasks, t_sizes, period))
        return stats
