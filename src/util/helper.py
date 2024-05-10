import datetime
import os


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
