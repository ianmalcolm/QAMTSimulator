# QAMTSimulator

Quantum Annealing Multitasking Simulator

Usage:

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

This is a python implementation of the work in the following paper:  
Huang, Tian and Zhu, Yongxin and Goh, Rick Siow Mong and Luo, Tao, When Quantum Annealing Meets Multitasking: Potentials, Challenges and Opportunities. Available at SSRN: https://ssrn.com/abstract=4252155 or http://dx.doi.org/10.2139/ssrn.4252155

Bibtex citation:  
```tex
@article{huang2022quantum,  
  title={When Quantum Annealing Meets Multitasking: Potentials, Challenges and Opportunities},  
  author={Huang, Tian and Zhu, Yongxin and Rick, Goh Siow Mong and Luo, Tao},  
  journal={SSRN},  
  year={2022}  
}  
```
