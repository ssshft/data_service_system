import json
import re
import threading
import traceback
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
from tools.LogEngine import log_engine


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
        # cache connection params on the instance so a dropped connection can be
        # re-established later from receive_redis_msg() without re-reading config
        self.redis_host = self.config.get_redis_host()
        self.redis_port = self.config.get_redis_port()
        self.redis_password = self.config.get_redis_password()
        self.physical_pub_channel = self.config.get_redis_physical_sub_channel()
        self.overview_pub_channel = self.config.get_redis_overview_pub_channel()

        self.subscribe_redis()
        self.receive_thread = threading.Thread(target=self.receive_redis_msg, daemon=True)
        self.receive_thread.start()

    def subscribe_redis(self):

        log_engine.warning(
            f'subscribe_redis called! thread={threading.current_thread().name} '
            f'time={time.time()}\n' + ''.join(traceback.format_stack())
        )

        # (re)create the redis connection and pubsub subscription; used both for the
        # initial connect and for reconnecting after the connection drops
        if len(self.redis_password) > 0:
            self.re = redis.StrictRedis(host=self.redis_host, port=self.redis_port,
                                         password=self.redis_password,
                                         socket_timeout=5, socket_connect_timeout=5)
        else:
            self.re = redis.StrictRedis(host=self.redis_host, port=self.redis_port,
                                         socket_timeout=5, socket_connect_timeout=5)
        self.pub = self.re.pubsub()
        self.pub.subscribe(self.physical_pub_channel)
        self.pub.subscribe(self.overview_pub_channel)

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

    def get_net_value_data(self, account_id, start_time, end_time):
        return self.data_base.get_net_value_data(account_id, start_time, end_time)

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
        retry_delay = 1
        while True:
            try:
                data = self.pub.parse_response()
                retry_delay = 1  # reset backoff once the connection is healthy again
            except Exception as e:
                print('parse response 2222222')
                log_engine.warning(f'redis pubsub connection error, will retry in {retry_delay}s: {e}')
                sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 30)
                try:
                    self.subscribe_redis()
                except Exception as reconnect_error:
                    log_engine.warning(f'redis reconnect failed: {reconnect_error}')
                continue

            if data:
                print('11111111111111111')
                print(data)
                if type(data[2]) is not int:
                    try:
                        redis_data = json.loads(data[2].decode('UTF-8'))
                        ty = redis_data.get('type', 0)
                        if ty == 4:
                            data_queue.add_view_data(redis_data)
                        elif ty == 1:
                            data_queue.add_detail_data(redis_data)
                    except Exception as e:
                        # a single malformed message should not take the subscriber thread down
                        log_engine.warning(f'failed to parse account redis message: {e}')

data_service = DataService()

if __name__ == '__main__':
    print('run')
