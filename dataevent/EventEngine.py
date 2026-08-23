from collections import defaultdict
from queue import Empty, Queue
from threading import Thread
from time import sleep

from dataevent.Const import TIMER_EVENT
from datasource.gateway.CtpObject import Event


class EventEngine:
    def __init__(self, interval=1):
        self._interval = interval
        self._queue = Queue()
        self._active = False
        self._thread = Thread(target=self._run)
        # self._timer = Thread(target=self._run_timer)
        self._handlers = defaultdict(list)
        self._general_handlers = []
        self.start()

    def _run(self) -> None:
        while self._active:
            try:
                event = self._queue.get(block=True, timeout=1)
                self._process(event)
            except Empty:
                pass

    def _process(self, event: Event) -> None:
        if event.type in self._handlers:
            [handler(event) for handler in self._handlers[event.type]]

        if self._general_handlers:
            [handler(event) for handler in self._general_handlers]

    def _run_timer(self) -> None:
        while self._active:
            sleep(self._interval)
            event = Event(TIMER_EVENT, "")
            self.put(event)

    def start(self) -> None:
        self._active = True
        self._thread.start()
        # self._timer.start()

    def stop(self) -> None:
        self._active = False
        self._thread.join()
        # self._timer.join()

    def put(self, event) -> None:
        self._queue.put(event)

    def register(self, type, handler) -> None:
        handler_list = self._handlers[type]
        if handler not in handler_list:
            handler_list.append(handler)

    def unregister(self, type, handler) -> None:
        handler_list = self._handlers[type]

        if handler in handler_list:
            handler_list.remove(handler)

        if not handler_list:
            self._handlers.pop(type)

    def register_general(self, handler) -> None:
        if handler not in self._general_handlers:
            self._general_handlers.append(handler)

    def unregister_general(self, handler) -> None:
        if handler in self._general_handlers:
            self._general_handlers.remove(handler)

