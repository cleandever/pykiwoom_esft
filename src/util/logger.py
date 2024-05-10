import os
import logging
import time


from py_singleton import singleton


@singleton
class Logger:
    log = None
    log_filename = '../../temp.log'

    def __init__(self):
        Logger.log = Logger._init_logger()

    @classmethod
    def write(cls, msg: object, level: object = 'info', write_to_bot: object = False, exc_info: object = 1) -> object:
        Logger()
        if level == 'warning':
            Logger.log.warning(msg)
        elif level == 'error':
            Logger.log.error(msg, exc_info=exc_info)
        else:
            Logger.log.info(msg)

        if write_to_bot:
            try:
                Logger.write_to_bot(msg)
            except Exception as e:
                Logger.write(e, level='error')
            finally:
                time.sleep(0.01)

    @classmethod
    def write_error(cls, msg, exception=''):
        Logger()
        Logger.log.error(f'{msg} - {exception}', exc_info=1)

    @classmethod
    def _init_logger(cls):
        # 로그 생성
        logger = logging.getLogger()

        # 로그의 출력 기준 설정
        logger.setLevel(logging.INFO)

        # log 출력 형식
        formatter = logging.Formatter('[%(asctime)s.%(msecs)03d][%(levelname)s] %(message)s', '%H:%M:%S')

        # log 출력
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        log_filename = 'my.log'
        if os.path.isfile(log_filename):
            os.remove(log_filename)

        # log를 파일에 출력
        file_handler = logging.FileHandler(Logger.log_filename, encoding='UTF-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger
