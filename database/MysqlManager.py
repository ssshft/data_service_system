import os
import re
import datetime
import pymysql
import pandas as pd


class MysqlManager():
    def __init__(self, host, port, user, password, data_base_name):
        super(MysqlManager, self).__init__()
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.data_base_name = data_base_name
        self.db = None
        self.cursor = None
        # self.connect()

    def connect(self):
        self.db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                  db=self.data_base_name, charset='utf8')
        self.cursor = self.db.cursor()
    
    def get_gateio_all_max_loan_data(self, account_name):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_gateio_max_loan where account_name='{account_name}'"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            account_id = res[1]
            account_name = res[2]
            currency = res[3]
            amount = float(res[4])
            gmt_updated = res[6].strftime('%Y-%m-%d %H:%M:%S')

            data.append([account_id, account_name, currency, amount, gmt_updated])
        cursor.close()
        my_db.close()
        return data

    def get_gateio_all_market_max_loan_data(self):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_gateio_market_max_loan"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            currency = res[1]
            rate = float(res[2])
            prec = float(res[3])
            discount = float(res[4])
            min_borrow_amount = float(res[5])
            user_max_borrow_amount = float(res[6])
            total_max_borrow_amount = float(res[7])
            price = float(res[8])
            status = res[9]
            gmt_create = res[10]
            gmt_updated = res[11].strftime('%Y-%m-%d %H:%M:%S')

            data.append([currency, rate, prec, discount, min_borrow_amount, user_max_borrow_amount, total_max_borrow_amount, price, status, gmt_create, gmt_updated])
        cursor.close()
        my_db.close()
        return data

    def get_okx_all_max_loan_data(self, account_name):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_okx_max_loan where account_name='{account_name}'"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            account_id = res[1]
            account_name = res[2]
            inst_id = res[3]
            mgn_mode = res[4]
            mgn_ccy = res[5]
            max_loan = float(res[6])
            ccy = res[7]
            side = res[8]
            gmt_updated = res[10].strftime('%Y-%m-%d %H:%M:%S')
            data.append([account_id, account_name, inst_id, mgn_mode, mgn_ccy, max_loan, ccy, side, gmt_updated])
        cursor.close()
        my_db.close()
        return data

    def get_binance_all_contract_info_data(self):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_binance_contract_info"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            inst_id = res[1]
            funding_rate_interval = float(res[2])
            gmt_updated = res[4].strftime('%Y-%m-%d %H:%M:%S')
            data.append([inst_id, funding_rate_interval, gmt_updated])
        cursor.close()
        my_db.close()
        return data

    def get_gateio_all_contract_info_data(self):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_gateio_contract_info"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            inst_id = res[1]
            funding_rate_interval = float(res[2])
            gmt_updated = res[4].strftime('%Y-%m-%d %H:%M:%S')
            data.append([inst_id, funding_rate_interval, gmt_updated])
        cursor.close()
        my_db.close()
        return data
    
    def get_bybit_all_contract_info_data(self):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_bybit_contract_info"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            inst_id = res[1]
            funding_rate_interval = float(res[2])
            gmt_updated = res[4].strftime('%Y-%m-%d %H:%M:%S')
            data.append([inst_id, funding_rate_interval, gmt_updated])
        cursor.close()
        my_db.close()
        return data
    
    def get_okx_all_contract_info_data(self):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_okx_contract_info"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            inst_id = res[1]
            funding_rate_interval = float(res[2])
            gmt_updated = res[4].strftime('%Y-%m-%d %H:%M:%S')
            data.append([inst_id, funding_rate_interval, gmt_updated])
        cursor.close()
        my_db.close()
        return data

    def get_binance_funding_rate_data(self, inst_id, start_time, end_time):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_binance_funding_rate where inst_id='{inst_id}' and funding_time>='{start_time}' and funding_time<'{end_time}' order by funding_time desc"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            inst_id = res[1]
            funding_rate = float(res[2])
            funding_time = res[3]
            data.append([inst_id, funding_rate, funding_time])
        cursor.close()
        my_db.close()
        return data

    def get_binance_all_funding_rate_data(self, start_time, end_time):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_binance_funding_rate where funding_time>='{start_time}' and funding_time<='{end_time}' order by funding_time desc"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            inst_id = res[1]
            funding_rate = float(res[2])
            funding_time = res[3]
            gmt_updated = res[5].strftime('%Y-%m-%d %H:%M:%S')
            data.append([inst_id, funding_rate, funding_time, gmt_updated])
        cursor.close()
        my_db.close()
        return data

    def get_gateio_funding_rate_data(self, inst_id, start_time, end_time):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_gateio_funding_rate where inst_id='{inst_id}' and funding_time>='{start_time}' and funding_time<'{end_time}' order by funding_time desc"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            inst_id = res[1]
            funding_rate = float(res[2])
            funding_time = res[3]
            data.append([inst_id, funding_rate, funding_time])
        cursor.close()
        my_db.close()
        return data
    
    def get_gateio_all_funding_rate_data(self, start_time, end_time):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_gateio_funding_rate where funding_time>='{start_time}' and funding_time<'{end_time}' order by funding_time desc"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            inst_id = res[1]
            funding_rate = float(res[2])
            funding_time = res[3]
            gmt_updated = res[5].strftime('%Y-%m-%d %H:%M:%S')
            data.append([inst_id, funding_rate, funding_time, gmt_updated])
        cursor.close()
        my_db.close()
        return data

    def get_bybit_funding_rate_data(self, inst_id, start_time, end_time):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_bybit_funding_rate where inst_id='{inst_id}' and funding_time>='{start_time}' and funding_time<'{end_time}' order by funding_time desc"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            inst_id = res[1]
            funding_rate = float(res[2])
            funding_time = res[3]
            data.append([inst_id, funding_rate, funding_time])
        cursor.close()
        my_db.close()
        return data
    
    def get_bybit_all_funding_rate_data(self, start_time, end_time):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_bybit_funding_rate where funding_time>='{start_time}' and funding_time<'{end_time}' order by funding_time desc"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            inst_id = res[1]
            funding_rate = float(res[2])
            funding_time = res[3]
            gmt_updated = res[5].strftime('%Y-%m-%d %H:%M:%S')
            data.append([inst_id, funding_rate, funding_time, gmt_updated])
        cursor.close()
        my_db.close()
        return data
    
    def get_okx_funding_rate_data(self, inst_id, start_time, end_time):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_okx_funding_rate where inst_id='{inst_id}' and funding_time>='{start_time}' and funding_time<'{end_time}' order by funding_time desc"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            inst_id = res[1]
            funding_rate = float(res[2])
            funding_time = res[3]
            data.append([inst_id, funding_rate, funding_time])
        cursor.close()
        my_db.close()
        return data
    
    def get_okx_all_funding_rate_data(self, start_time, end_time):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_okx_funding_rate where funding_time>='{start_time}' and funding_time<'{end_time}' order by funding_time desc"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            inst_id = res[1]
            funding_rate = float(res[2])
            funding_time = res[3]
            gmt_updated = res[5].strftime('%Y-%m-%d %H:%M:%S')
            data.append([inst_id, funding_rate, funding_time, gmt_updated])
        cursor.close()
        my_db.close()
        return data

    def get_binance_kline_data(self, inst_id, start_time, end_time):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_binance_kline where inst_id='{inst_id}' and kline_time>='{start_time}' and kline_time<'{end_time}' order by kline_time desc"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            inst_id = res[1]
            open_price = float(res[2])
            high_price = float(res[3])
            low_price = float(res[4])
            close_price = float(res[5])
            volume = float(res[6])
            turnover = float(res[7])
            kline_time = res[8]
            data.append([inst_id, open_price, high_price, low_price, close_price, volume, turnover, kline_time])
        cursor.close()
        my_db.close()
        return data
    
    def get_binance_all_kline_data(self, start_time, end_time):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_binance_kline where kline_time>='{start_time}' and kline_time<='{end_time}' order by kline_time desc"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            inst_id = res[1]
            open_price = float(res[2])
            high_price = float(res[3])
            low_price = float(res[4])
            close_price = float(res[5])
            volume = float(res[6])
            turnover = float(res[7])
            kline_time = res[8]
            gmt_updated = res[10].strftime('%Y-%m-%d %H:%M:%S')
            data.append([inst_id, open_price, high_price, low_price, close_price, volume, turnover, kline_time, gmt_updated])
        cursor.close()
        my_db.close()
        return data
    
    def get_binance_kline_1m_data(self, inst_id, start_time, end_time):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_binance_kline_1m where inst_id='{inst_id}' and kline_time>='{start_time}' and kline_time<'{end_time}' order by kline_time desc"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            inst_id = res[1]
            open_price = float(res[2])
            high_price = float(res[3])
            low_price = float(res[4])
            close_price = float(res[5])
            volume = float(res[6])
            turnover = float(res[7])
            kline_time = res[8]
            data.append([inst_id, open_price, high_price, low_price, close_price, volume, turnover, kline_time])
        cursor.close()
        my_db.close()
        return data
    
    def get_binance_all_kline_1m_data(self, start_time, end_time):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_binance_kline_1m where kline_time>='{start_time}' and kline_time<'{end_time}' order by kline_time desc"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            inst_id = res[1]
            open_price = float(res[2])
            high_price = float(res[3])
            low_price = float(res[4])
            close_price = float(res[5])
            volume = float(res[6])
            turnover = float(res[7])
            kline_time = res[8]
            data.append([inst_id, open_price, high_price, low_price, close_price, volume, turnover, kline_time])
        cursor.close()
        my_db.close()
        return data

    def get_gateio_kline_data(self, inst_id, start_time, end_time):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_gateio_kline where inst_id='{inst_id}' and kline_time>='{start_time}' and kline_time<'{end_time}' order by kline_time desc"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            inst_id = res[1]
            open_price = float(res[2])
            high_price = float(res[3])
            low_price = float(res[4])
            close_price = float(res[5])
            volume = float(res[6])
            turnover = float(res[7])
            kline_time = res[8]
            data.append([inst_id, open_price, high_price, low_price, close_price, volume, turnover, kline_time])
        cursor.close()
        my_db.close()
        return data
    
    def get_gateio_all_kline_data(self, start_time, end_time):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_gateio_kline where kline_time>='{start_time}' and kline_time<'{end_time}' order by kline_time desc"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            inst_id = res[1]
            open_price = float(res[2])
            high_price = float(res[3])
            low_price = float(res[4])
            close_price = float(res[5])
            volume = float(res[6])
            turnover = float(res[7])
            kline_time = res[8]
            gmt_updated = res[10].strftime('%Y-%m-%d %H:%M:%S')
            data.append([inst_id, open_price, high_price, low_price, close_price, volume, turnover, kline_time, gmt_updated])
        cursor.close()
        my_db.close()
        return data

    def get_bybit_kline_data(self, inst_id, start_time, end_time):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_bybit_kline where inst_id='{inst_id}' and kline_time>='{start_time}' and kline_time<'{end_time}' order by kline_time desc"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            inst_id = res[1]
            open_price = float(res[2])
            high_price = float(res[3])
            low_price = float(res[4])
            close_price = float(res[5])
            volume = float(res[6])
            turnover = float(res[7])
            kline_time = res[8]
            data.append([inst_id, open_price, high_price, low_price, close_price, volume, turnover, kline_time])
        cursor.close()
        my_db.close()
        return data
    
    def get_bybit_all_kline_data(self, start_time, end_time):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_bybit_kline where kline_time>='{start_time}' and kline_time<'{end_time}' order by kline_time desc"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            inst_id = res[1]
            open_price = float(res[2])
            high_price = float(res[3])
            low_price = float(res[4])
            close_price = float(res[5])
            volume = float(res[6])
            turnover = float(res[7])
            kline_time = res[8]
            gmt_updated = res[10].strftime('%Y-%m-%d %H:%M:%S')
            data.append([inst_id, open_price, high_price, low_price, close_price, volume, turnover, kline_time, gmt_updated])
        cursor.close()
        my_db.close()
        return data
    
    def get_bybit_kline_data_close_price(self, inst_id, kline_time):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        close_price = 0
        sql = f"select * from t_bybit_kline where inst_id='{inst_id}' and kline_time='{kline_time}'"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            close_price = float(res[5])
        cursor.close()
        my_db.close()
        return close_price

    def get_binance_open_interest_data(self, inst_id, start_time, end_time):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_binance_open_interest where inst_id='{inst_id}' and bar_time>='{start_time}' and bar_time<'{end_time}' order by bar_time desc"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            inst_id = res[1]
            open_interest = float(res[2])
            open_interest_value = float(res[3])
            bar_time = res[4]
            data.append([inst_id, open_interest, open_interest_value, bar_time])
        cursor.close()
        my_db.close()
        return data
    
    def get_binance_all_open_interest_data(self, start_time, end_time):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_binance_open_interest where bar_time>='{start_time}' and bar_time<='{end_time}' order by bar_time desc"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            inst_id = res[1]
            open_interest = float(res[2])
            open_interest_value = float(res[3])
            bar_time = res[4]
            gmt_updated = res[6].strftime('%Y-%m-%d %H:%M:%S')
            data.append([inst_id, open_interest, open_interest_value, bar_time, gmt_updated])
        cursor.close()
        my_db.close()
        return data

    def get_gateio_open_interest_data(self, inst_id, start_time, end_time):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_gateio_open_interest where inst_id='{inst_id}' and bar_time>='{start_time}' and bar_time<'{end_time}' order by bar_time desc"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            inst_id = res[1]
            open_interest = float(res[2])
            open_interest_value = float(res[3])
            bar_time = res[4]
            data.append([inst_id, open_interest, open_interest_value, bar_time])
        cursor.close()
        my_db.close()
        return data
    
    def get_gateio_all_open_interest_data(self, start_time, end_time):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_gateio_open_interest where bar_time>='{start_time}' and bar_time<'{end_time}' order by bar_time desc"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            inst_id = res[1]
            open_interest = float(res[2])
            open_interest_value = float(res[3])
            bar_time = res[4]
            gmt_updated = res[6].strftime('%Y-%m-%d %H:%M:%S')
            data.append([inst_id, open_interest, open_interest_value, bar_time, gmt_updated])
        cursor.close()
        my_db.close()
        return data

    def get_bybit_open_interest_data(self, inst_id, start_time, end_time):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_bybit_open_interest where inst_id='{inst_id}' and bar_time>='{start_time}' and bar_time<'{end_time}' order by bar_time desc"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            inst_id = res[1]
            open_interest = float(res[2])
            open_interest_value = float(res[3])
            bar_time = res[4]
            data.append([inst_id, open_interest, open_interest_value, bar_time])
        cursor.close()
        my_db.close()
        return data
    
    def get_bybit_all_open_interest_data(self, start_time, end_time):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_bybit_open_interest where bar_time>='{start_time}' and bar_time<'{end_time}' order by bar_time desc"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            inst_id = res[1]
            open_interest = float(res[2])
            open_interest_value = float(res[3])
            bar_time = res[4]
            gmt_updated = res[6].strftime('%Y-%m-%d %H:%M:%S')
            data.append([inst_id, open_interest, open_interest_value, bar_time, gmt_updated])
        cursor.close()
        my_db.close()
        return data
    
    def get_net_value_data(self, account_id, start_time, end_time):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_rad_net_value where account_id='{account_id}' and record_time>='{start_time}' and record_time<'{end_time}' order by record_time desc"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            account_id = res[1]
            net_value = float(res[2])
            daily_return = float(res[3])
            record_time = res[4]
            data.append([account_id, net_value, daily_return, record_time])
        cursor.close()
        my_db.close()
        return data

    def get_trade_risk_info_data(self, account_name, start_time, end_time):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_trade_risk_info where account_name='{account_name}' and gmt_create>='{start_time}' and gmt_create<='{end_time}'"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            account_id = int(res[1])
            account_name = res[2]
            base_asset = res[3]
            net_value = float(res[4])
            risk_exposure = float(res[5])
            leverage = float(res[6])
            gmt_create = res[7]
            data.append([account_id, account_name, base_asset, net_value, risk_exposure, leverage, gmt_create])
        cursor.close()
        my_db.close()
        return data
    
    def get_binance_account_income_data(self, account_id, ty, start_time, end_time):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_binance_account_income where account_id='{account_id}' and income_time>='{start_time}' and income_time<'{end_time}' and income_type='{ty}'"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            account_id = res[1]
            inst_id = res[2]
            inst_type = res[3]
            income_type = res[4]
            income_change = float(res[5])
            asset = res[6]
            income_time = res[8]
            data.append([account_id, inst_id, inst_type, income_type, income_change, asset, income_time])
        cursor.close()
        my_db.close()
        return data
    
    def get_gateio_account_income_data(self, account_id, ty, start_time, end_time):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_gateio_account_income where account_id='{account_id}' and income_time>='{start_time}' and income_time<'{end_time}' and income_type='{ty}'"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            account_id = res[1]
            inst_id = res[2]
            inst_type = res[3]
            income_type = res[4]
            income_change = float(res[5])
            balance = float(res[6])
            income_time = res[8]
            data.append([account_id, inst_id, inst_type, income_type, income_change, balance, income_time])
        cursor.close()
        my_db.close()
        return data

    def get_bybit_account_income_data(self, account_id, ty, start_time, end_time):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        sql = f"select * from t_bybit_account_income where account_id='{account_id}' and income_time>='{start_time}' and income_time<'{end_time}' and income_type='{ty}'"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            account_id = res[1]
            inst_id = res[3]
            inst_type = res[4]
            income_type = res[5]
            income_change = float(res[6])
            funding = float(res[7])
            fee = float(res[8])
            cash_flow = float(res[9])
            income_time = res[10]
            data.append([account_id, inst_id, inst_type, income_type, income_change, funding, fee, cash_flow, income_time])
        cursor.close()
        my_db.close()
        return data
    
    def get_okx_account_income_data(self, account_id, ty, start_time, end_time):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        data = []
        ty_str = ','.join(ty)
        sql = f"select * from t_okx_account_income where account_id='{account_id}' and income_time>='{start_time}' and income_time<'{end_time}' and income_type in ({ty_str})"
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            account_id = res[1]
            inst_id = res[3]
            inst_type = res[4]
            income_type = res[5]
            income_change = float(res[6])
            fee = float(res[7])
            interest = float(res[8])
            pnl = float(res[9])
            ccy = res[10]
            income_time = res[11]
            data.append([account_id, inst_id, inst_type, income_type, income_change, fee, interest, pnl, ccy, income_time])
        cursor.close()
        my_db.close()
        return data


    


    def list_tables(self):
        my_db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                db=self.data_base_name, charset='utf8')
        cursor = my_db.cursor()
        sql = f"show tables"
        cursor.execute(sql)
        results = cursor.fetchall()
        print(results)
        cursor.close()
        my_db.close()

    def close(self):
        self.cursor.close()
        self.db.close()


if __name__ == '__main__':
    print('run')