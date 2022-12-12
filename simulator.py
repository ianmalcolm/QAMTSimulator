import logging

class QAMTSimulator:

    def __init__(self, tasks, annealer, scheduler):

        self.logger = logging.getLogger(__name__)

        self.annealer = annealer
        self.scheduler = scheduler

        self.task_queue = sorted(tasks, key=lambda t: t.getTimeArrive())
        self.task_ready = []
        self.task_complete = []

        self.instruction_queue = []
        self.instruction_complete = []

        self.time = None


    def isComplete(self):
        """ Check if all tasks are complete
        """
        flag = len(self.task_queue) == 0
        flag &= len(self.task_ready) == 0
        return flag


    def fastForward(self):
        """ Fast forward the time of the simulation to the next event if
        """
        if len(self.task_ready) == 0 and len(self.instruction_queue) == 0:
            self.time = self.task_queue[0].getTimeArrive()


    def getTime(self):
        return self.time


    def checkReadyTasks(self):
        """ Check if any queued tasks is available and move them to the
            ready list
        """
        task_r = [t for t in self.task_queue if t.getTimeArrive() <= self.time]
        for t in task_r:
            self.task_queue.remove(t) 
            self.logger.info(f'{t} is ready', extra={'sim_time': self.time})

        if task_r:
            self.logger.info(f'Remain {len(self.task_queue)} tasks in queue.', extra={'sim_time': self.time})

        self.task_ready.extend(task_r)


    def checkCompleteTasks(self):
        """ Check if any task in ready list is complete, and move them
            to the complete list
        """
        task_c = [t for t in self.task_ready if t.isComplete()]
        for t in task_c:
            self.task_ready.remove(t) 
            self.logger.info(f'{t} is complete', extra={'sim_time': self.time})

        if task_c:
            self.logger.info(f'Remain {len(self.task_ready)} tasks in ready list.', extra={'sim_time': self.time})

        self.task_complete.extend(task_c)


    def enqueueInstructions(self, insts):
        if insts:
            self.logger.info(f'Enqueue {len(insts)} instructions', extra={'sim_time': self.time})
            self.instruction_queue.extend(insts)


    def dequeueInstruction(self):
        inst = self.instruction_queue.pop(0)
        tasks = inst.getTasks()
        self.logger.info(f'Dequeue instruction for {tasks}', extra={'sim_time': self.time})
        return inst


    def execInstruction(self, annealer, inst):
        self.time = annealer.execute(inst, self.time)
        tasks = inst.getTasks()
        self.logger.info(f'Execute instruction for {tasks}', extra={'sim_time': self.time})


    def logInstruction(self, inst):
        self.instruction_complete.append(inst)
        tasks = inst.getTasks()
        self.logger.info(f'Log instruction for {tasks}', extra={'sim_time': self.time})


    def run(self):
        """ Run the simulation
        """

        while not self.isComplete():

            self.fastForward()

            # Find available tasks in queue and move to ready list
            self.checkReadyTasks()

            insts = self.scheduler.schedule(self.task_ready, self.annealer)
            self.enqueueInstructions(insts)
            inst = self.dequeueInstruction()
            self.execInstruction(self.annealer, inst)
            self.logInstruction(inst)

            # Find complete tasks in ready list and move to complete list
            self.checkCompleteTasks()


    def getInstructionComplete(self):
        return self.instruction_complete.copy()


