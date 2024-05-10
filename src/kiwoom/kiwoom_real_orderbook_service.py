import time

from src.thread_service import ThreadService


class KiwoomRealOrderbookService(ThreadService):
    def __init__(self, kiwoom_wrapper, stock_code, callback_orderbook):
        super().__init__(service_name='KiwoomRealOrderbookService',
                         service_idle_seconds=0,
                         service_start_time='090000',
                         service_end_time='152000')
        self.kiwoom_wrapper = kiwoom_wrapper
        self.stock_code = stock_code
        self.callback_orderbook = callback_orderbook

    def start_service(self):
        super().start_service()
        self.kiwoom_wrapper.register_real(self.stock_code)

    def stop_service(self):
        super().stop_service()
        self.kiwoom_wrapper.unregister_real()

    def task(self):
        while not self.service_stop_event.is_set():
            data = self.kiwoom_wrapper.km.get_real_no_blocking()
            if data:
                self.callback_orderbook(self.kiwoom_wrapper, self.stock_code, data)
            time.sleep(0.01)
