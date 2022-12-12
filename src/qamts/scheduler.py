from .instruction import QMI
from .scheduling_algorithms import firstFit, nextFit, randomFit


class ToyScheduler:

    def __init__(self):
        pass

    def schedule(self, tasks, annealer):

        t = tasks[0]

        res = annealer.getRes()
        name, demand, dur = t.getReq()
        assert demand.shape[0] <= res.shape[0] and demand.shape[1] <= res.shape[1], f'Resource requirement {demand.shape} should be smaller than the number of resources available in the processor {res.shape}.'
        res[:demand.shape[0], :demand.shape[1]] = 1
        sched = [(name, res, dur)]
        inst = QMI.fromSched(sched)
        inst.setNumReads(t.getNumSamples())

        return [inst]


class StaticScheduler:

    def __init__(self):
        """ Static scheduler assumes that all tasks are available at time 0.
            It maximises the resource utilisation.
        """
        pass

    def schedule(self, tasks, annealer):
        if len(tasks) == 0:
            return []

        reqs = [t.getReq() for t in tasks]
        reqs = sorted(reqs, key=lambda x: (-x[1].sum(), -x[2]))
        scheds = nextFit(reqs, annealer.getRes())

        if len(scheds) == 0:
            return []

        insts = [QMI.fromSched(scheds[0])] if scheds else []
        return insts


class NaiveScheduler:


    def __init__(self):
        """ This dynamic scheduler assumes time of task arrival varies.
            It allocates resources roughly according to task priority and
            maximises resource utilisation. Every schedule it produces only
            last for a specified interval.

        """
        pass


    def schedule(self, tasks, annealer):

        if len(tasks) == 0:
            return []

        res = annealer.getRes()
        name, demand, dur = tasks[0].getReq()
        res[:demand.shape[0], :demand.shape[1]] = 1
        sched = [(name, res, dur)]

        inst = QMI.fromSched(sched)

        size_sample = [(t.getEmbd().size, t.getNumSamples()) for t in inst.getTasks()]
        _, num_samples = sorted(size_sample, key=lambda x: (-x[0], x[1]))[0]

        inst.setNumReads(num_samples)

        return [inst]
    

class NextFitTaskPreemption:


    def __init__(self):
        """ This dynamic scheduler assumes time of task arrival varies.
            It allocates resources roughly according to task priority and
            maximises resource utilisation. Every schedule it produces only
            last for a specified interval.

        """


    def schedule(self, tasks, annealer):

        if len(tasks) == 0:
            return []

        res = annealer.getRes()
        reqs = [t.getReq() for t in tasks]
        sched = []
        while True:

            new_sched = nextFit(reqs, res, n_schedules=1)[0]
            if len(new_sched) == 0:
                break
            else:
                sched.extend(new_sched)
                for _, alloc, _ in new_sched:
                    res += alloc

        inst = QMI.fromSched(sched)

        size_sample = [(t.getEmbd().size, t.getNumSamples()) for t in inst.getTasks()]
        _, num_samples = sorted(size_sample, key=lambda x: (-x[0], x[1]))[0]

        inst.setNumReads(num_samples)

        return [inst]


class DynamicScheduler:


    def __init__(self, n_samples=500):
        """ This dynamic scheduler assumes time of task arrival varies.
            It allocates resources roughly according to task priority and
            maximises resource utilisation. Every schedule it produces only
            last for a specified interval.

        Args:
          n_samples: only schedule the next n samples no matter how many
                     samples are required by the tasks. If set to None, it
                     is equivalent to static scheduling.
        """
        self.n_samples=n_samples


    def schedule(self, tasks, annealer, priority=None):

        if len(tasks) == 0:
            return []

        reqs = []

        reqs = [t.getReq() for t in tasks]
        scheds = randomFit(reqs, annealer.getRes(), priority)

        inst = QMI.fromSched(scheds[0])

        if self.n_samples:
            num_reads = self.n_samples
        else:
            num_reads = min(t.getNumReads() for t in inst.getTasks())

        inst.setNumReads(num_reads)

        return inst
