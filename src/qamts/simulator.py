import logging

class QAMTSimulator:

    def __init__(self, tasks, annealer, scheduler, static_scheduling=False):

        self.logger = logging.getLogger(__name__)

        self.annealer = annealer
        self.scheduler = scheduler

        self.time = 0
        self.event_queue = []

        if static_scheduling:
            for t in tasks:
                t.setTimeArrive(0)
        for t in tasks:
            self.enqueue_event(Event.taskReady(t))
        
        self.task_queue = [t for t in tasks]
        self.task_ready = []
        self.task_run = []
        self.task_complete = []

        self.instruction_queue = []
        self.instruction_complete = []


    def dequeue_event(self):
        t = self.event_queue[0].time
        events = [e for e in self.event_queue if e.time == t]
        self.event_queue = [e for e in self.event_queue if e.time > t]
        return t, events


    def enqueue_event(self, e):
        if e.time is None:
            e.time = self.time
        self.event_queue.insert(0, e)
        self.event_queue = sorted(self.event_queue, key=lambda x: x.time)


    def isComplete(self):
        """ Check if all tasks are complete
        """
        return len(self.event_queue)==0


    def getTime(self):
        return self.time


    def enqueueInstructions(self, insts):
        if insts:
            self.logger.info(f'Enqueue {len(insts)} instructions', extra={'sim_time': self.time})
            self.instruction_queue.extend(insts)


    def dequeueInstruction(self):
        inst = self.instruction_queue.pop(0)
        tasks = inst.getTasks()
        self.logger.info(f'Dequeue instruction for {tasks}', extra={'sim_time': self.time})
        return inst


    def handleTaskEvent(self, e):
        if e.type == Event.TASK_READY:
            # put task into ready list
            task = e.data
            self.task_queue.remove(task) 
            self.task_ready.append(task)
            self.logger.info(f'{task} is ready', extra={'sim_time': self.time})

        elif e.type == Event.TASK_RUN:
            pass
        else: # e.type == Event.TASK_COMP
            task = e.data
            self.task_ready.remove(task) 
            self.task_complete.append(task)
            self.logger.info(f'{task} is complete', extra={'sim_time': self.time})


    def handleInstEvent(self, e):
        if e.type == Event.INST_READY:
            inst = e.data

            tasks = inst.getTasks()
            for t in list(set(tasks)):
                self.task_run.append(t)
                self.task_ready.remove(t)
            self.logger.info(f'Execute instruction for {tasks}', extra={'sim_time': self.time})
            finish_time = self.annealer.execute(inst, self.time)

            self.annealer.setBusy()
            self.enqueue_event(Event.instComp(inst, finish_time))
        elif e.type == Event.INST_RUN:
            pass
        else: # e.type == Event.INST_COMP

            inst = e.data
            self.instruction_complete.append(inst)
            tasks = inst.getTasks()
            for t in list(set(tasks)):
                self.task_run.remove(t)
                self.task_ready.append(t)
            self.logger.info(f'Log instruction for {tasks}', extra={'sim_time': self.time})

            self.annealer.setIdle()
            for task in self.task_ready:
                if task.isComplete():
                    self.enqueue_event(Event.taskComp(task))


    def run(self):
        """ Run the simulation
        """

        while not self.isComplete():

            self.time, events = self.dequeue_event()

            # task related events
            task_events = [e for e in events if e.isTaskEvent()]
            for e in task_events:
                self.handleTaskEvent(e)

            # generate and issue inst if annealer is idle
            if self.task_ready and self.annealer.isIdle():
                insts = self.scheduler.schedule(self.task_ready, self.annealer)
                events.append(Event.instReady(insts[0], self.time))
            
            # instruction related events
            inst_events = [e for e in events if e.isInstEvent()]
            for e in inst_events:
                self.handleInstEvent(e)

            # print(self.time, self.event_queue)


    def getInstructionComplete(self):
        return self.instruction_complete.copy()


class Event:

    TASK_READY=1
    TASK_RUN=2
    TASK_COMP=3

    INST_READY=4
    INST_RUN=5
    INST_COMP=6

    def __init__(self, _time, _type, data):
        self.time = _time
        self.type = _type
        self.data = data


    def __repr__(self):
        return f'({self.time},{self.type},{self.data})'


    @staticmethod
    def taskReady(task, time=None):
        e = Event(time or task.getTimeArrive(), 
                  Event.TASK_READY,
                  task)
        return e


    @staticmethod
    def taskComp(task, time=None):
        e = Event(time, 
                  Event.TASK_COMP,
                  task)
        return e


    @staticmethod
    def instReady(inst, time=None):
        e = Event(time, 
                  Event.INST_READY,
                  inst)
        return e


    @staticmethod
    def instComp(inst, time=None):
        e = Event(time, 
                  Event.INST_COMP,
                  inst)
        return e


    def isTaskEvent(self):
        return self.type in [Event.TASK_READY, Event.TASK_RUN, Event.TASK_COMP]



    def isInstEvent(self):
        return self.type in [Event.INST_READY, Event.INST_RUN, Event.INST_COMP]
