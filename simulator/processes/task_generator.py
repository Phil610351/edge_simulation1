from abc import abstractmethod
from collections import deque
from simulator.core.task import Task
from simulator.config import Config
from simulator.common import Common
from simulator.core.process import Process
import numpy as np

class TaskGeneratorPlug:
    
    @abstractmethod
    def fetchTaskDistributionTimeQueue(self, processId: int) -> deque:
        pass
    
    @abstractmethod
    def taskNodeId(self, processId: int) -> int:
        pass
    
    @abstractmethod
    def taskArrival(self, task: Task, processId: int) -> None:
        pass
    
class TaskGenerator(Process):
    def __init__(self, plug: TaskGeneratorPlug) -> None:
        super().__init__()
        self._plug = plug
        self._loadCongif()
        
    def _loadCongif(self):
        self._mode_tasks_from_task_list = Config.get("mode_tasks_from_task_list")
        self._task_size_kBit = Config.get("task_size_kBit")
        self._task_size_sd_kBit = Config.get("task_size_sd_kBit")
        self._task_size_min_kBit = Config.get("task_size_min_kBit")
        self._task_kflops_per_bit = Config.get("task_kflops_per_bit")
        self._task_kflops_per_bit_sd = Config.get("task_kflops_per_bit_sd")
        self._task_kflops_per_bit_min = Config.get("task_kflops_per_bit_min")
    
    def wake(self) -> None:
        super().wake()
        timeQueue = self._plug.fetchTaskDistributionTimeQueue(self.id())
        while(len(timeQueue) > 0 and timeQueue[0] <= Common.time()):
            timeQueue.popleft()
            self.generateTask()
            
    def generateTask(self) -> Task:
        TaskGenerator.retrieveConfig()
        if TaskGenerator._mode_tasks_from_task_list:
            return TaskGenerator._listTask(self._plug, self._id)
        else:
            return TaskGenerator._randomTask(self._plug, self._id)
    
    @classmethod
    def _randomTask(cls, plug: TaskGeneratorPlug, id: int) -> Task:
        taskSize, flops = cls.generateTaskTuple()
        newTask = Task(taskSize, flops, plug.taskNodeId(id), Common.time())
        plug.taskArrival(newTask, id)
    
    @classmethod
    def _listTask(cls, plug: TaskGeneratorPlug, id: int) -> Task:
        cls.retrieveList()
        taskSize, flops =cls._tupleList[np.random.randint(0, len(cls._tupleList))]
        newTask = Task(taskSize, flops, plug.taskNodeId(id), Common.time())
        plug.taskArrival(newTask, id)
    
    @classmethod
    def retrieveList(cls):
        cls.retrieveConfig()
        if not hasattr(cls, "_list_retrieved"):
            cls._list_retrieved = True
            cls._tupleList = []
            listsize = Config.get("task_from_task_list_listsize")
            for i in range(0, listsize):
                cls._tupleList.append(cls.generateTaskTuple())
    
    @classmethod
    def generateTaskTuple(cls):
        #TODO: try other distributions
        taskSize = np.random.normal(cls._task_size_kBit, cls._task_size_sd_kBit) * 1000
        taskSize = int(max([cls._task_size_min_kBit * 1000, taskSize]))
        flops = np.random.normal(cls._task_kflops_per_bit, cls._task_kflops_per_bit_sd) * 1000
        flops = int(max([cls._task_kflops_per_bit_min * 1000, flops]))
        return (taskSize, flops)
    
    @classmethod
    def retrieveConfig(cls):
        if not hasattr(cls, "_config_retrieved"):
            cls._config_retrieved = True
            cls._mode_tasks_from_task_list = Config.get("mode_tasks_from_task_list")
            cls._task_size_kBit = Config.get("task_size_kBit")
            cls._task_size_sd_kBit = Config.get("task_size_sd_kBit")
            cls._task_size_min_kBit = Config.get("task_size_min_kBit")
            cls._task_kflops_per_bit = Config.get("task_kflops_per_bit")
            cls._task_kflops_per_bit_sd = Config.get("task_kflops_per_bit_sd")
            cls._task_kflops_per_bit_min = Config.get("task_kflops_per_bit_min")
            
    
    