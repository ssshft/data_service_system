import codecs
import os
import threading
import time
from datetime import datetime
from random import random

import chardet


def convert_to_utf8(file, out_enc="UTF-8"):  # 将文件格式转化为utf-8
    if not os.path.exists(file):
        return

    with open(file, "rb") as f:
        data = f.read()
        code_type = chardet.detect(data)['encoding']
        in_enc = code_type.upper()
        out_enc = out_enc.upper()
        try:
            f_code = codecs.open(file, 'r', in_enc, "ignore")
            new_content = f_code.read()
            codecs.open(file, 'w', out_enc).write(new_content)
        except IOError as err:
            print("I/O error: {0}".format(err))


def get_program_path():
    program_path = os.path.dirname(os.path.dirname((os.path.abspath(__file__))))
    return program_path


def get_cwd_path():
    current_path = os.getcwd()
    return current_path


def create_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)


def convert_to_datetime(input_value):
    convert_value = input_value
    if isinstance(input_value, str):
        convert_value = datetime.strptime(input_value.replace('-', '').replace('/', '-'), '%Y%m%d')
    return convert_value


# 生产者线程
class Producer(threading.Thread):
    def __init__(self, t_name, queue):
        threading.Thread.__init__(self, name=t_name)
        self.data = queue

    def run(self):
        for i in range(5):
            print("%s: %s is producing %d to the queue!" % (time.ctime(), self.getName(), i))
            self.data.put(i)  # 将生产的数据放入队列
            time.sleep(random.randrange(10) / 5)
        print("%s: %s finished!" % (time.ctime(), self.getName()))


# 消费者线程
class Consumer(threading.Thread):
    def __init__(self, t_name, queue):
        threading.Thread.__init__(self, name=t_name)
        self.data = queue

    def run(self):
        for i in range(5):
            val = self.data.get()  # 拿出已经生产好的数据
            print("%s: %s is consuming. %d in the queue is consumed!" % (time.ctime(), self.getName(), val))
            time.sleep(random.randrange(5))
            self.data.task_done()  # 告诉队列有关这个数据的任务已经处理完成
        print("%s: %s finished!" % (time.ctime(), self.getName()))


if __name__ == '__main__':
    print(get_cwd_path())
