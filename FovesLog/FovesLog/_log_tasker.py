import time
import logging

class LoggedTask:
    """ 一个可以记录用时的工具 """
    def __init__(self, 
                 task_name: str, 
                 logger: logging.Logger|None=None, 
                 level: int=logging.INFO,
                 time_precision: int=2,
                 ) -> None:
        self.task_name = task_name
        self.level = level
        self.time_precision = time_precision
        self.logger = logger or logging.getLogger(f'任务-{task_name}')

        self.start_time: float
        self.last_checkpoint: float
    
    def __enter__(self):
        self.logger.log(self.level, f'任务 {self.task_name} 开始')
        self.start_time = time.time()
        self.last_checkpoint = time.time()
        return self
    
    def checkpoint(self, message: str):
        self.logger.log(self.level, f'{message}, 用时 {time.time()  - self.last_checkpoint:.{self.time_precision}f} 秒')
        self.last_checkpoint = time.time()

    def __exit__(self, exc_type, exc, tb):
        self.logger.log(self.level, f'任务 {self.task_name} 完成，用时 {time.time() - self.start_time:.{self.time_precision}f} 秒')
        