import threading
from time import sleep
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger


class TaskScheduler:
    _instance_lock = threading.Lock()

    def __init__(self):
        super(TaskScheduler, self).__init__()
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

    def __new__(cls, *args, **kwargs):
        if not hasattr(TaskScheduler, "_instance"):
            with TaskScheduler._instance_lock:
                if not hasattr(TaskScheduler, "_instance"):
                    TaskScheduler._instance = object.__new__(cls)
        return TaskScheduler._instance

    def add_cron_job(self, func, hour, minute, args=None):
        self.scheduler.add_job(func=func, trigger='cron', args=args, hour=hour, minute=minute, misfire_grace_time=3600)

    def add_one_time_job(self, func, args, next_run_time):
        self.scheduler.add_job(func=func, args=args, next_run_time=next_run_time)

    def add_repeat_job(self, func, seconds, args=None, id=None):
        trigger = IntervalTrigger(seconds=seconds)
        self.scheduler.add_job(func=func, trigger=trigger, args=args, id=id)

    def remove_job_by_id(self, id):
        self.scheduler.remove_job(id)


def print_msg(msg1, msg2):
    print(msg1)
    print(msg2)


if __name__ == '__main__':
    task_scheduler = TaskScheduler()
    task_scheduler.add_repeat_job(print_msg, 3, ['ttt', 1])
    while True:
        sleep(5)
