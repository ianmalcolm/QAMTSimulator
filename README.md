# QAMTSimulator

QAMTSimulator stands for Quantum Annealing Multitasking Simulator.

This simulator is for simulating Multitasking on Quantum Annealing devices. Multitasking would improve the resource utilisation of quantum annealers. The capacity of quantum computers has been scaled up several thousand times in the past two decades. We believe that the need for QAMT also increases along with the capacity of a quantum annealer. Time-critical applications such as automation control and autonomous driving would benefit from QAMT, as the execution time of tasks is known. Multitasking would also enable virtualisation of quantum annealers, allowing multiple users to share a quantum annealer without knowing the existence of other users. The sharing of quantum annealers would reduce the cost of usage and spark new applications and opportunities.

We employ a lot of terminologies from [D-Wave](https://www.dwavesys.com/) quantum annealing systems. But the simulator applies to any quantum computing system that adopt ``Array of unit cells`` design methodology.


## Introduction

We develop an event-based QAMTS simulator in Python that serves as a platform to evaluate scheduling algorithms for QAMT. The figure below shows the diagram of the simulator. It takes a series of tasks as input. A QAMT scheduler combines one or multiple tasks into an instruction. The scheduler may consider the status of the annealer when translating tasks into instructions. The instructions are fed into an annealer and executed sequentially.

<p align="center">
<img src="images/qamts.png" alt="Diagram of QAMTSimulator" width="66%"/>
</p>

To facilitate the development and evaluation of various scheduling algorithms, we implemented a few visualisation tools along with the simulator. These tools inspect scheduling from a space allocation and time scheduling point of view.

<p align="center">
<img src="images/temporal.png" alt="Temporal scheduling" width="66%"/>
</p>

The figure above shows the schedule of time slice produced by a scheduling algorithm.  X axis is time, Y axis is resource utilisation. A long vertical bar has a few segments, which indicate the space in that period is shared by a few tasks.

<p align="center">
<img src="images/spatial.png" alt="Spatial scheduling" width="66%"/>
</p>

The figure above shows the spatial aspect of tasks achieved by the demo schedule. The device has a 16x16 unit cells. A gray block represents the resource occupied by a task.




## Usage

```python
#import a few modules
from qamts.simulator import QAMTSimulator
from qamts.scheduler import ToyScheduler
from qamts.annealer import Chimera
from qamts.instruction import QMI
from qamts.task import Task
from qamts.utils import randomTasks

#Randomly generate a set of tasks
tasks = randomTasks(4, anneal_time=100, seed=0)
tasks = Task.load(tasks)

#Create an instance of processor with 16x16 unit cells
processor = Chimera()

#Create an instance of a toy scheduler
scheduler = ToyScheduler()

#Create an instance of the simulator.
sim = QAMTSimulator(
    tasks,
    processor,
    scheduler,
)

#Run it
sim.run()
    
```

For more detailed usage, please check this [example](examples/example.ipynb)

## Citation

This is a python implementation of the work in the following paper:  
Huang, Tian and Zhu, Yongxin and Goh, Rick Siow Mong and Luo, Tao, When Quantum Annealing Meets Multitasking: Potentials, Challenges and Opportunities. Available at  [here](https://doi.org/10.1016/j.array.2023.100282)

Bibtex citation:  
```tex
@article{huang2023quantum,
title = {When quantum annealing meets multitasking: Potentials, challenges and opportunities},
journal = {Array},
volume = {17},
pages = {100282},
year = {2023},
issn = {2590-0056},
doi = {https://doi.org/10.1016/j.array.2023.100282},
url = {https://www.sciencedirect.com/science/article/pii/S2590005623000073},
author = {Tian Huang and Yongxin Zhu and Rick Siow Mong Goh and Tao Luo},
keywords = {Quantum annealing, Multitasking},
abstract = {Quantum computers have provided a promising tool for tackling NP hard problems. However, most of the existing work on quantum annealers assumes exclusive access to all resources available in a quantum annealer. This is not resource efficient if a task consumes only a small part of an annealer and leaves the rest wasted. We ask if we can run multiple tasks in parallel or concurrently on an annealer, just like the multitasking capability of a classical general-purpose processor. By far, multitasking is not natively supported by any of the existing annealers. In this paper, we explore Multitasking in Quantum Annealer (QAMT) by identifying the parallelism in a quantum annealer from the aspect of space and time. Based on commercialised quantum annealers from D-Wave, we propose a realisation scheme for QAMT, which packs multiple tasks into a quantum machine instruction (QMI) and uses predefined sampling time to emulate task preemption. We enumerate a few scheduling algorithms that match well with QAMT and discuss the challenges in QAMT. To demonstrate the potential of QAMT, we simulate a quantum annealing system, implement a demo QAMT scheduling algorithm, and evaluate the algorithm. Experimental results suggest that there is great potential in multitasking in quantum annealing.}
}  
```
