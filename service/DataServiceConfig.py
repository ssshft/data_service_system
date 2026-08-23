import threading
from configparser import ConfigParser
import os
from tools.Utility import get_program_path


class DataServieConfig:
    _instance_lock = threading.Lock()

    def __init__(self):
        self.mysql_host = ''
        self.mysql_port = ''
        self.mysql_user = ''
        self.mysql_password = ''
        self.mysql_name = ''
        self.redis_host = ''
        self.redis_port = ''
        self.redis_password = ''
        self.physical_pub_channel = ''
        self.overview_pub_channel = ''
        program_path = get_program_path()
        config_path = os.path.join(program_path, 'config/dataservice.ini')
        self.read_config(config_path)

    def __new__(cls, *args, **kwargs):
        if not hasattr(DataServieConfig, "_instance"):
            with DataServieConfig._instance_lock:
                if not hasattr(DataServieConfig, "_instance"):
                    DataServieConfig._instance = object.__new__(cls)
        return DataServieConfig._instance

    def read_config(self, config_path):
        if not os.path.exists(config_path):
            print(f'config file: {config_path} does not exist!')
        else:
            config = ConfigParser()
            config.read(config_path)
            sections = config.sections()
            if 'Mysql' in sections:
                self.mysql_host = config.get('Mysql', 'host')
                self.mysql_port = config.get('Mysql', 'port')
                self.mysql_user = config.get('Mysql', 'user')
                self.mysql_password = config.get('Mysql', 'password')
                self.mysql_name = config.get('Mysql', 'name')
            if 'Redis' in sections:
                self.redis_host = config.get('Redis', 'host')
                self.redis_port = config.get('Redis', 'port')
                self.redis_password = config.get('Redis', 'password')
                self.physical_pub_channel = config.get('Redis', 'physicalpubchannel')
                self.overview_pub_channel = config.get('Redis', 'overviewpubchannel')

    def get_mysql_host(self):
        return self.mysql_host

    def get_mysql_port(self):
        return int(self.mysql_port)

    def get_mysql_user(self):
        return self.mysql_user

    def get_mysql_password(self):
        return self.mysql_password

    def get_mysql_name(self):
        return self.mysql_name

    def get_redis_host(self):
        return self.redis_host

    def get_redis_port(self):
        return self.redis_port

    def get_redis_password(self):
        return self.redis_password

    def get_redis_physical_sub_channel(self):
        return self.physical_pub_channel
    
    def get_redis_overview_pub_channel(self):
        return self.overview_pub_channel


if __name__ == '__main__':
    data_service_config = DataServieConfig()
