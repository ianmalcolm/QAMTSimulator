#!/usr/bin/env python

import pytest

from qamts.simulator import QAMTSimulator
from qamts.scheduler import ToyScheduler
from qamts.annealer import Chimera
from qamts.instruction import QMI
from qamts.task import Task
from qamts.utils import randomTasks

def test_main():

    tasks = randomTasks(4, anneal_time=100, seed=0)

    sim = QAMTSimulator(
        Task.load(tasks),
        Chimera(),
        ToyScheduler(),
    )

    sim.run()

if __name__ == '__main__':
    test_main()