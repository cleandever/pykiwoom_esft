import time

from src.util.thread_service import ThreadService


class KiwoomRealMarketOpenTimeService(ThreadService):
    def __init__(self, kiwoom_wrapper, callback_market_open_time):
        super().__init__(service_name='KiwoomRealMarketOpenTimeService',
                         service_idle_seconds=0,
                         service_start_time='060000',
                         service_end_time='152000')
        self.kiwoom_wrapper = kiwoom_wrapper
        self.callback_market_open_time = callback_market_open_time

    def start_service(self):
        super().start_service()
        self.kiwoom_wrapper.register_real_market_open_time()

    def stop_service(self):
        super().stop_service()
        self.kiwoom_wrapper.unregister_real()

    def task(self):
        while not self.service_stop_event.is_set():
            data = self.kiwoom_wrapper.km.get_real_no_blocking()
            if data:
                self.callback_market_open_time(data)
            time.sleep(0.01)
