import datetime
import queue
import time
import traceback

import telegram
import threading

from telegram.ext import Updater, CommandHandler


class LogTelegramSender:
    def __init__(self, chat_id, bot):
        self.chat_id = chat_id
        self.bot = bot

        self.msgs = queue.Queue()
        self.tx_thread = threading.Thread(target=self.tx_service_worker)
        self.service_stop_event = threading.Event()
        self.total_handle_count = 0

    def add_msg(self, msg):
        self.msgs.put(msg)

    def tx_service_worker(self):
        while not self.service_stop_event.is_set():
            msg_len = self.msgs.qsize()
            if msg_len:
                self.tx_msg_handler(msg_len)
            time.sleep(0.1)

    def tx_msg_handler(self, msg_len):
        for _ in range(msg_len):
            msg = self.msgs.get()
            try:
                self.bot.sendMessage(chat_id=self.chat_id, text=msg)
            except Exception as e:
                print(f'error - exception - {e}, trace : {traceback.format_exc()}')
            self.total_handle_count += 1

    def start_service(self):
        self.tx_thread.start()

    def stop_service(self):
        self.service_stop_event.set()


class LogTelegramReceiver:
    def __init__(self, token):
        self.token = token

        ## updater
        self.updater = Updater(token=self.token, use_context=True)
        self.dispatcher = self.updater.dispatcher

        self.handler_id_auto_increment = 0

        self.handlers = dict()

        self.updater.start_polling()

    def add_handler(self, menu_name, callback_func):
        handler_id = str(self.handler_id_auto_increment)
        self.handler_id_auto_increment += 1

        handler = CommandHandler([menu_name, handler_id], callback_func)
        self.dispatcher.add_handler(handler)
        print(f'텔레그램 메뉴 등록 - menu_name : {menu_name}, callback_func : {callback_func}')

    def start_service(self):
        self.updater.start_polling()

    def stop_service(self):
        self.updater.stop()
        self.updater.is_idle = False


class LogTelegram:
    def __init__(self, chat_id, token):
        self.chat_id = chat_id
        self.token = token
        self.bot = telegram.Bot(self.token)

        self.log_telegram_sender = LogTelegramSender(self.chat_id, self.bot)
        self.log_telegram_receiver = LogTelegramReceiver(self.token)

    def start_service(self):
        self.log_telegram_sender.start_service()
        self.log_telegram_receiver.start_service()
        print('텔레그램 서비스 시작')

    def stop_service(self):
        self.log_telegram_sender.stop_service()
        self.log_telegram_receiver.stop_service()
        print('텔레그램 서비스 종료')

    def write(self, msg):
        # msg reformat
        msg = msg.replace(' - ', '\n')
        msg = msg.replace(', ', '\n')
        msg += f"\n{datetime.datetime.now().strftime('%H:%M:%S.%f')}"
        self.log_telegram_sender.add_msg(msg)

    def add_receiver_handler(self, menu_name, callback_func):
        # 메뉴 이름에 공백이 들어가면 안됨
        if ' ' in menu_name:
            return False
        self.log_telegram_receiver.add_handler(menu_name, callback_func)
        return True
