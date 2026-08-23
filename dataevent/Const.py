from enum import Enum


class Direction(Enum):
    LONG = "多"
    SHORT = "空"
    NET = "净"


class Offset(Enum):
    NONE = ""
    OPEN = "开"
    CLOSE = "平"
    CLOSETODAY = "平今"
    CLOSEYESTERDAY = "平昨"


class Status(Enum):
    SUBMITTING = "提交中"
    NOTTRADED = "未成交"
    PARTTRADED = "部分成交"
    ALLTRADED = "全部成交"
    CANCELLED = "已撤销"
    REJECTED = "拒单"


class OrderType(Enum):
    LIMIT = "限价"  # 执行时必须按照限定价格或更好的价格成交的指令
    MARKET = "市价"  # 按当时市场价格即刻成交的指令
    STOP = "STOP"  # 当市场价格达到客户预先设定的触发价格时，变为市价指令予以执行
    FAK = "FAK"  # 立即全部成交否则自动撤销指令 在限定价位下下达指令
    FOK = "FOK"  # 立即成交剩余指令自动撤销指令 在限定价位下下达指令


class Exchange(Enum):
    CFFEX = "CFFEX"  # China Financial Futures Exchange
    SHFE = "SHFE"  # Shanghai Futures Exchange
    CZCE = "CZCE"  # Zhengzhou Commodity Exchange
    DCE = "DCE"  # Dalian Commodity Exchange
    INE = "INE"  # Shanghai International Energy Exchange
    SSE = "SSE"  # Shanghai Stock Exchange
    SZSE = "SZSE"  # Shenzhen Stock Exchange
    SGE = "SGE"  # Shanghai Gold Exchange
    WXE = "WXE"  # Wuxi Steel Exchange


class Product(Enum):
    EQUITY = "股票"
    FUTURES = "期货"
    OPTION = "期权"
    INDEX = "指数"
    FOREX = "外汇"
    SPOT = "现货"
    ETF = "ETF"
    BOND = "债券"
    WARRANT = "权证"
    SPREAD = "价差"
    FUND = "基金"


TICK_EVENT = "tick_event"
ORDER_EVENT = "order_event"
TRADE_EVENT = "trade_event"
POSITION_EVENT = "position_event"
ACCOUNT_EVENT = "account_event"
CONTRACT_EVENT = "contract_event"
TIMER_EVENT = "timer_event"
LOG_EVENT = "log_event"
INVESTOR_EVENT = "investor_event"
INVESTOR_UNIT_EVENT = "investor_unit_event"
INSTRUMENT_COMMISSION_EVENT = "instrument_commission_event"
INSTRUMENT_MARGIN_EVENT = "instrument_margin_event"
EXCHANGE_EVENT = "exchange_event"
INSTRUMENT_EXCHANGE_MARGIN_EVENT = "instrument_exchange_margin_event"
INSTRUMENT_EXCHANGE_MARGIN_ADJUST_EVENT = "instrument_exchange_margin_adjust_event"

SCRIPT_LOG_EVENT = "script_log_event"

traders_setting = {
    "ctp": {"front_address": "", "broker_id": "", "user_id": "", "password": "", "app_id": "", "auth_code": "",
            "product_info": ""},
    "xtp": {}}

mds_setting = {
    "ctp": {"front_address": "", },
    "xtp": {}
}

exchanges = {
    "SHFE": "上海期货交易所",
    "CZCE": "郑州商品交易所",
    "DCE": "大连商品交易所",
    "CFFEX": "中国金融期货交易所",
    "INE": "上海国际能源交易中心股份有限公司"
}

exchanges_type = {
    "0": "正常",
    "1": "根据成交生成报单"
}

directions = {
    "buy": "多",
    "sell": "空"
}

offsets = {
    "open": "开",
    "cover": "平",
    "cover_today": "平今",
    "cover_yesterday": "平左"
}

order_types = {
    "limit": "限价",
    "market": "市价",
    "stop": "STOP",
    "fak": "FAK",
    "fok": "FOK"
}


def get_all_traders():
    return traders_setting.keys()


def get_setting_by_trader(trader):
    setting = {}
    if trader in traders_setting.keys():
        setting = traders_setting[trader]

    return setting


def get_all_mds():
    return mds_setting.keys()


def get_setting_by_md(md):
    setting = {}
    if md in mds_setting.keys():
        setting = mds_setting[md]
    return setting


def get_all_exchanges():
    return exchanges.keys()


def get_all_directions():
    return directions.keys()


def get_all_offsets():
    return offsets.keys()


def get_all_order_types():
    return order_types.keys()