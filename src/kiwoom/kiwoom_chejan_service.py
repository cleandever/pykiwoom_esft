import time

from src.util.thread_service import ThreadService


class KiwoomChejanService(ThreadService):
    def __init__(self, kiwoom_wrapper, callback_chejan):
        super().__init__(service_name='KiwoomChejanService',
                         service_idle_seconds=0,
                         service_start_time='090000',
                         service_end_time='152000')
        self.kiwoom_wrapper = kiwoom_wrapper
        self.callback_chejan = callback_chejan

    def task(self):
        while not self.service_stop_event.is_set():
            data = self.kiwoom_wrapper.km.get_chejan_no_blocking()
            if data:
                self.callback_chejan(self.kiwoom_wrapper, data)
            time.sleep(0.05)
