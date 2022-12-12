import numpy as np


def randomTasks(num=1,
                embd_size=(12,12),
                anneal_time=2000,
                sample_range=list(range(100, 1100, 100)),
                seed=None):
    """ Generate tasks in the form of list of dict
    """
    
    if isinstance(seed, int):
        rng = np.random.default_rng(seed)
    elif isinstance(seed, np.random._generator.Generator):
        rng = seed
    else:
        rng = np.random.default_rng()
    
    numbering_length = len(str(num))
    names = [f't{i:0{numbering_length}d}' for i in range(num)]

    anneal_rows, anneal_cols = embd_size
    embd_rows = rng.integers(1, anneal_rows, size=num,endpoint=True)
    embd_cols = embd_rows + rng.integers(-2,2,size=num,endpoint=True)
    embd_cols = np.clip(embd_cols, 1, anneal_cols)

    num_reads = rng.choice(sample_range, size=num, replace=True)

    anneal_times = [anneal_time for i in range(num)]

    t_arrives = [int(t - t % anneal_time) for t in np.linspace(0, num/4*np.mean(sample_range)*anneal_time, num)]
    
    task_list = []
    for n, _rows, _cols, r, neal, arr in zip(names, embd_rows, embd_cols, num_reads, anneal_times, t_arrives):
        task = {
            'name': n,
            'embd': f'np.ones(({_rows},{_cols}), dtype=int)',
            'num_reads': int(r),
            'anneal_time': neal,
            't_arrive': arr,
        }
        task_list.append(task)

    return task_list

