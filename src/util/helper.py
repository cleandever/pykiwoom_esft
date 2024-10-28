import datetime
import os
import sys

import psutil as psutil

from src.util.logger import Logger


class Helper:
    @classmethod
    def get_init_log_filename(cls, log_filename_prefix='', log_dir='./log'):
        now_ymd = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)
        if log_filename_prefix:
            return f'{log_dir}/{now_ymd}_{log_filename_prefix}.log'
        return f'{log_dir}/{now_ymd}.log'

    @classmethod
    def is_time_between(cls, start_time, end_time):
        now = datetime.datetime.now()
        now_time = now.strftime('%H%M%S')
        if start_time <= now_time <= end_time:
            return True
        return False

    @classmethod
    def is_now_time_over(cls, time):
        now = datetime.datetime.now()
        now_time = now.strftime('%H%M%S')
        if time < now_time:
            return True
        return False

    @classmethod
    def is_now_time_under(cls, time):
        now = datetime.datetime.now()
        now_time = now.strftime('%H%M%S')
        if now_time < time:
            return True
        return False

    @classmethod
    def terminate_current_process(cls):
        """현재 프로세스와 모든 자식 프로세스를 안전하게 종료"""
        try:
            current_process = psutil.Process(os.getpid())

            # 1. 자식 프로세스 종료
            children = current_process.children(recursive=True)
            for child in children:
                Helper.terminate_process_safely(child, is_child=True)

            # 2. 현재 프로세스 종료
            Helper.terminate_process_safely(current_process, is_child=False)

        except Exception as e:
            Logger.write(f'프로세스 종료 작업 실패: {str(e)}')
            sys.exit(1)

    @classmethod
    def terminate_process_safely(cls, process, is_child=True):
        """단일 프로세스를 안전하게 종료하는 함수

        Args:
            process (psutil.Process): 종료할 프로세스 객체
            is_child (bool): 자식 프로세스 여부
        """
        process_type = "child" if is_child else "parent"
        Logger.write(f'{process_type} 프로세스 강제종료 - {process.name()} (PID: {process.pid})')
        try:
            process.terminate()
            process.wait(timeout=3)

        except psutil.TimeoutExpired:
            Logger.write(f'{process_type} 프로세스 응답 없음 - 강제 종료 시도')
            process.kill()
        except psutil.NoSuchProcess:
            Logger.write(f'{process_type} 프로세스가 이미 종료됨')
        except Exception as e:
            Logger.write(f'{process_type} 프로세스 종료 중 예외 발생: {str(e)}')
            raise
