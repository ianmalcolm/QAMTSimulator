import numpy as np
from scipy.signal import convolve2d


def randomFit(tasks: list, resources: np.ndarray, priorities=None):
    """ Random fit with priority

    Args:
      tasks: A list of tuples, in the format of (name, demand, duration)
            where demand is a 2D bitmap resource requirement, duration is
            the period the task is going to last for.
      resources: A 2D bitmap of resource usage of the target processor.
            1 means the resource is occupied
      priorities: a list of positive numbers. None means equal priority.

    Returns:
      The schedule of tasks, in the form of
            [[(n0,alloc0,dur0),...], [(n8,alloc8,dur8),...], ...]
    """

    taskq = tasks.copy()
    pq = priorities.copy() if priorities else [1] * len(taskq)

    cdf = [sum(pq[:i]) for i, _ in enumerate(pq, start=1)]
    cdf = np.asarray([0] + cdf) / cdf.max()

    schedule = resources.copy(), []

    while taskq:

        i = np.digitize(np.random.rand(), cdf) - 1
        alloc = nextFit([taskq[i]], res, n_schedules=1)

        if alloc is None:
            # This task i can no longer fit into the schedule, remove it
            taskq.pop(i)
            pq.pop(i)
            # Regenerate the cdf
            cdf = [sum(pq[:i]) for i, _ in enumerate(pq, start=1)]
            cdf = np.asarray([0] + cdf) / cdf.max()
        else:
            schedule[0] += alloc
            schedule[1].append(taskq[i])

    return [schedule[1]]


def nextFit(tasks: list, resources: np.ndarray, n_schedules=None):
    """ Next fit

    Args:
      tasks: A list of tuples, in the format of (name, demand, duration)
            where demand is a 2D bitmap resource requirement, duration is
            the period the task is going to last for.
      resources: A 2D bitmap of resource usage of the target processor.
            1 means the resource is occupied
      n_schedules: only produce n schedules. This saves computation
            effort if you only want the first few schedules.

    Returns:
      The schedule of tasks, in the form of
            [[(n0,alloc0,dur0),...], [(n8,alloc8,dur8),...], ...]

    """
    taskq = tasks.copy()
    schedules = [(resources.copy(), [])]

    while len(taskq):

        res, subset = schedules[-1]
        ind_task = None

        for i, (name, demand, duration) in enumerate(taskq):
            alloc = fitDemandWithRotateFlip(res, demand)
            if alloc is not None:
                # find a fit
                ind_task = i, (name, alloc, duration)
                break
        else:
            # not enough space, add another schedule
            if n_schedules and len(schedules) >= n_schedules:
                break
            else:
                schedules.append((resources.copy(), []))

        if len(subset) == 0 and ind_task is None:
            raise ValueError(f'Failed to fit remaining tasks {taskq}')

        if ind_task is not None:
            i, (name, alloc, duration) = ind_task 
            res += alloc
            subset.append((name, alloc, duration))
            taskq.pop(i)

    return [subset for _, subset in schedules]


def firstFit(tasks: list, resources: np.ndarray):
    """ First fit

    Args:
      tasks: A list of tuples, in the format of (name, demand, duration)
            where demand is a 2D bitmap resource requirement, duration is
            the period the task is going to last for.
      resources: A 2D bitmap of resource usage of the target processor.
            1 means the resource is occupied

    Returns:
      The schedule of tasks, in the form of
            [[(n0,alloc0,dur0),...], [(n8,alloc8,dur8),...], ...]

    """
    taskq = tasks.copy()
    schedules = [(resources.copy(), [])]

    while len(taskq):
        name, demand, duration = taskq.pop(0)
        for res, subset in schedules:
            alloc = fitDemandWithRotateFlip(res, demand)
            if alloc is not None:
                res += alloc
                subset.append((name, alloc, duration))
                break
        else:
            res = resources.copy()
            subset = []
            alloc = fitDemandWithRotateFlip(res, demand)
            if alloc is not None:
                res += alloc
                subset.append((name, alloc, duration))
                schedules.append((res, subset))
            else:
                raise ValueError(f'Failed to fit {name}')

    return [subset for _, subset in schedules]


def fitDemandWithRotateFlip(res: np.ndarray, dmd: np.ndarray):
    """ Given resource usage and resource demand, fit demand with rotation
        and flip. Allow irregular shape demand.

    Args:
      res: a 2D bitmap of resource usage. 1 means occupied.
      dmd: a 2D bitmap of demand. 1 means required.

    Returns:
      alloc: a 2D bitmap of resouce allocation. 1 means allocated resource.
             If fit not found, return None
    """

    best = None, 0

    if np.all(dmd):
        # a rectangle shape
        for angle90 in [0, 1]:
            dmdt = np.rot90(dmd,  k=angle90)
            alloc, score = fitDemand(res, dmdt, return_score=True)
            if score > best[1]:
                best = alloc, score
    else:
        # an irregular shape
        for angle90 in [0, 1, 2, 3]:
            for flip in [True, False]:
                dmdt = np.rot90(dmd,  k=angle90)
                dmdt = np.fliplr(dmdt) if flip else dmdt
                alloc, score = fitDemand(res, dmdt, return_score=True)
                if score > best[1]:
                    best = alloc, score

    return best[0]


def fitDemand(res: np.ndarray, dmd: np.ndarray, return_score=False):
    """ Given resource usage and resource demand, fit demand
        Allow irregular shape demand.

    Args:
      res: a 2D bitmap of resource usage. 1 means occupied.
      dmd: a 2D bitmap of demand. 1 means required.
      return_score: indicate if return score

    Returns:
      alloc: a 2D bitmap of resouce allocation. 1 means allocated resource
      score: the score of the fit, higher is better. 0 means does not fit
    """

    # prepare mask
    cross = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])

    # find feasible locations
    feasible = convolve2d(res, dmd, mode='valid')
    # padding ones to encourage edge fit
    feasible_pad = np.pad(feasible, 1, 'constant', constant_values=1)
    scores = convolve2d(feasible_pad, cross, mode='same')[1:-1, 1:-1]
    scores = (1-feasible.astype(bool)) * scores
    best_score = scores.max()

    if best_score > 0:
        ind = np.unravel_index(np.argmax(scores, axis=None), scores.shape)
        ind0_start, ind0_end = ind[0], ind[0]+dmd.shape[0]
        ind1_start, ind1_end = ind[1], ind[1]+dmd.shape[1]
        alloc = np.zeros_like(res, dtype=int)
        alloc[ind0_start:ind0_end, ind1_start:ind1_end] += dmd
    else:
        alloc = None

    if return_score:
        return alloc, best_score
    else:
        return alloc
