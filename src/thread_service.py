import datetime
import threading
import time
from abc import abstractmethod

from src.util.logger import Logger


class ThreadService(threading.Thread):
    def __init__(self, service_name, service_idle_seconds,
                 service_start_time=None, service_end_time=None):
        super().__init__(name=service_name)
        assert service_idle_seconds == 0 or service_idle_seconds >= 1, \
            'service_idle_seconds must be greater than 1.'
        self.service_idle_seconds = service_idle_seconds
        self.service_stop_event = threading.Event()

        # HHMMSS
        self.service_start_time = service_start_time
        self.service_end_time = service_end_time

    def run(self):
        Logger.write(f'[{self.name}] 시작 - '
                     f'idle seconds : {self.service_idle_seconds}, '
                     f'서비스 시작 시간 : {self.service_start_time}, '
                     f'서비스 종료 시간 : {self.service_end_time}')
        self.wait_until_service_start_time()
        while not self.service_stop_event.is_set():
            try:
                self.task()
            except Exception as e:
                Logger.write_error(e)
            self.idle()
            self.check_service_end_time()
        Logger.write(f'[{self.name}] 종료')

    def wait_until_service_start_time(self):
        while self.service_start_time:
            now_time = datetime.datetime.now().strftime("%H%M%S")
            if self.service_start_time <= now_time:
                Logger.write(f'[{self.name}] 서비스 시작 시간 도달')
                break
            time.sleep(1)

    def check_service_end_time(self):
        if self.service_end_time:
            now_time = datetime.datetime.now().strftime("%H%M%S")
            if now_time > self.service_end_time:
                Logger.write(f'[{self.name}] 서비스 종료 시간 도달')
                self.stop_service()

    @abstractmethod
    def task(self):
        # do nothing
        pass

    def idle(self):
        for _ in range(self.service_idle_seconds):
            time.sleep(1)
            if self.service_stop_event.is_set():
                break

    def start_service(self):
        self.start()

    def stop_service(self):
        Logger.write(f'[{self.name}] 서비스 종료 이벤트 수신')
        self.service_stop_event.set()
