from abc import abstractmethod, ABC

from dataevent.Const import TICK_EVENT, ORDER_EVENT, TRADE_EVENT, POSITION_EVENT, ACCOUNT_EVENT, CONTRACT_EVENT, LOG_EVENT, \
    INVESTOR_EVENT, INSTRUMENT_COMMISSION_EVENT, EXCHANGE_EVENT, INSTRUMENT_MARGIN_EVENT, \
    INSTRUMENT_EXCHANGE_MARGIN_EVENT, INSTRUMENT_EXCHANGE_MARGIN_ADJUST_EVENT, INVESTOR_UNIT_EVENT
from datasource.gateway.CtpObject import Event


class DataHandler(ABC):
    def __init__(self, main_event):
        self.main_event = main_event

    def add_event(self, event_type, data):
        event = Event(event_type, data)
        self.main_event.put(event)

    def on_tick(self, data):
        self.add_event(TICK_EVENT, data)

    def on_order(self, data):
        self.add_event(ORDER_EVENT, data)

    def on_trade(self, data):
        self.add_event(TRADE_EVENT, data)

    def on_position(self, data):
        self.add_event(POSITION_EVENT, data)

    def on_account(self, data):
        self.add_event(ACCOUNT_EVENT, data)

    def on_contract(self, data):
        self.add_event(CONTRACT_EVENT, data)

    def on_log(self, data):
        self.add_event(LOG_EVENT, data)

    def on_investor(self, data):
        self.add_event(INVESTOR_EVENT, data)

    def on_investor_unit(self, data):
        self.add_event(INVESTOR_UNIT_EVENT, data)

    def on_instrument_commission_rate(self, data):
        self.add_event(INSTRUMENT_COMMISSION_EVENT, data)

    def on_instrument_margin_rate(self, data):
        self.add_event(INSTRUMENT_MARGIN_EVENT, data)

    def on_exchagne(self, data):
        self.add_event(EXCHANGE_EVENT, data)

    def on_instrument_exchange_margin_rate(self, data):
        self.add_event(INSTRUMENT_EXCHANGE_MARGIN_EVENT, data)

    def on_instrument_exchange_margin_rate_adjust(self, data):
        self.add_event(INSTRUMENT_EXCHANGE_MARGIN_ADJUST_EVENT, data)
