import logging
import os
import threading
from datetime import datetime

from tools.Utility import get_program_path, create_folder


class LogEngine:
    _instance_lock = threading.Lock()

    def __init__(self):
        super(LogEngine, self).__init__()
        self.logger = logging.getLogger('Log Engine')
        self.level = logging.INFO
        self.logger.setLevel(self.level)
        self.formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
        self.file_handler = None
        # self.add_console_handler()
        self.add_file_handler()

    def __new__(cls, *args, **kwargs):
        if not hasattr(LogEngine, "_instance"):
            with LogEngine._instance_lock:
                if not hasattr(LogEngine, "_instance"):
                    LogEngine._instance = object.__new__(cls)
        return LogEngine._instance

    def add_console_handler(self):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.level)
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)

    def add_file_handler(self):
        log_path = os.path.join(get_program_path(), 'log')
        create_folder(log_path)
        current_date_str = datetime.now().strftime('%Y%m%d')
        log_file = os.path.join(log_path, f'{current_date_str}_log.txt')
        self.file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        self.file_handler.setLevel(self.level)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

    def remove_file_handler(self):
        if self.file_handler:
            self.logger.removeHandler(self.file_handler)

    def reset_file_handler(self):
        self.remove_file_handler()
        self.add_file_handler()

    def critical(self, msg):
        self.logger.log(logging.CRITICAL, msg)

    def info(self, msg):
        self.logger.log(logging.INFO, msg)

    def warning(self, msg):
        self.logger.log(logging.WARNING, msg)


log_engine = LogEngine()


if __name__ == '__main__':
    log_engine.warning('warning')

