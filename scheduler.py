from instruction import QMI
from scheduling_algorithms import firstFit, nextFit, randomFit


class ToyScheduler:

    def __init__(self):
        pass

    def schedule(self, tasks, annealer):
        if len(tasks) > 0:
            return [QMI.fromTask(tasks[0])]
        else:
            return []


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
        reqs = sorted(reqs, key=lambda x: (-x[2], -x[1].sum()))
        scheds = nextFit(reqs, annealer.getRes())

        if len(scheds) == 0:
            return []

        insts = [QMI.fromSched(scheds[0])] if scheds else []
        return insts


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
