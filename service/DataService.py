import json
import re
import threading
import os
import sys
from datetime import datetime, timedelta
from time import sleep
import redis

path = os.path.dirname(os.path.dirname((os.path.abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)

from database.MysqlManager import MysqlManager
from service.DataServiceConfig import DataServieConfig
from dataevent.DataQueue import data_queue


class DataService:
    _instance_lock = threading.Lock()

    def __init__(self):
        self.data_source = None
        self.data_base = None
        self.re = None
        self.history_stock_info = {}
        self.stock_fundamental = {}
        self.config = DataServieConfig()
        self.connect_data_base()
        self.connect_redis()

    def __new__(cls, *args, **kwargs):
        if not hasattr(DataService, "_instance"):
            with DataService._instance_lock:
                if not hasattr(DataService, "_instance"):
                    DataService._instance = object.__new__(cls)
        return DataService._instance

    def connect_data_base(self):
        database_host = self.config.get_mysql_host()
        database_port = self.config.get_mysql_port()
        database_user = self.config.get_mysql_user()
        database_password = self.config.get_mysql_password()
        database_name = self.config.get_mysql_name()
        self.data_base = MysqlManager(database_host, database_port, database_user, database_password, database_name)

    def connect_redis(self):
        host = self.config.get_redis_host()
        port = self.config.get_redis_port()
        password = self.config.get_redis_password()
        physical_pub_channel = self.config.get_redis_physical_sub_channel()
        overview_pub_channel = self.config.get_redis_overview_pub_channel()

        if len(password) > 0:
            self.re = redis.StrictRedis(host=host, port=port, password=password)
        else:
            self.re = redis.StrictRedis(host=host, port=port)
        self.pub = self.re.pubsub()
        self.pub.subscribe(physical_pub_channel)
        self.pub.subscribe(overview_pub_channel)
        self.receive_thread = threading.Thread(target=self.receive_redis_msg)
        self.receive_thread.start()

    def get_gateio_all_market_max_loan_data(self):
        return self.data_base.get_gateio_all_market_max_loan_data()

    def get_stock_list(self):
        return self.data_base.get_stock_list()

    def get_stock_day_data(self, symbol, variable, start_date, end_date):
        return self.data_base.get_stock_day_data(symbol, variable, start_date, end_date)

    def get_stock_day_data_variables(self):
        return self.data_base.get_stock_day_data_variables()

    def get_stock_kline_data(self, symbol):
        return self.data_base.get_stock_kline_data(symbol)

    def get_future_kline_data(self, symbol):
        return self.data_base.get_future_kline_data(symbol)

    def get_future_close_data(self, symbol):
        return self.data_base.get_future_close_data(symbol)

    def get_future_money_data(self, current_date):
        return self.data_base.get_future_money_data(current_date)

    def get_gateio_market_max_loan(self):
        return self.data_base.get_gateio_all_market_max_loan_data()
    
    def get_gateio_max_loan(self, account_name):
        return self.data_base.get_gateio_all_max_loan_data(account_name)
    
    def get_okx_max_loan(self, account_name):
        return self.data_base.get_okx_all_max_loan_data(account_name)
    
    def get_binance_funding_rate(self, start_time, end_time):
        return self.data_base.get_binance_all_funding_rate_data(start_time, end_time)

    def get_gateio_funding_rate(self, start_time, end_time):
        return self.data_base.get_gateio_all_funding_rate_data(start_time, end_time)
    
    def get_bybit_funding_rate(self, start_time, end_time):
        return self.data_base.get_bybit_all_funding_rate_data(start_time, end_time)

    def get_okx_funding_rate(self, start_time, end_time):
        return self.data_base.get_okx_all_funding_rate_data(start_time, end_time)
    
    def get_binance_contract_info(self):
        return self.data_base.get_binance_all_contract_info_data()

    def get_gateio_contract_info(self):
        return self.data_base.get_gateio_all_contract_info_data()
    
    def get_bybit_contract_info(self):
        return self.data_base.get_bybit_all_contract_info_data()
    
    def get_okx_contract_info(self):
        return self.data_base.get_okx_all_contract_info_data()
    
    def get_binance_contract_open_interest(self, start_time, end_time):
        return self.data_base.get_binance_all_open_interest_data(start_time, end_time)
    
    def get_gateio_contract_open_interest(self, start_time, end_time):
        return self.data_base.get_gateio_all_open_interest_data(start_time, end_time)
    
    def get_bybit_contract_open_interest(self, start_time, end_time):
        return self.data_base.get_bybit_all_open_interest_data(start_time, end_time)

    def get_binance_kline(self, start_time, end_time):
        return self.data_base.get_binance_all_kline_data(start_time, end_time)

    def get_gateio_kline(self, start_time, end_time):
        return self.data_base.get_gateio_all_kline_data(start_time, end_time)
    
    def get_bybit_kline(self, start_time, end_time):
        return self.data_base.get_bybit_all_kline_data(start_time, end_time)
    
    def receive_redis_msg(self):
        while True:
            data = self.pub.parse_response()
            if data:
                if type(data[2]) is not int:
                    redis_data = json.loads(data[2].decode('UTF-8'))
                    ty = redis_data.get('type', 0)
                    if ty == 4:
                        data_queue.add_view_data(redis_data)
                    elif ty == 1:
                        data_queue.add_detail_data(redis_data)
                    

data_service = DataService()

if __name__ == '__main__':
    print('run')
