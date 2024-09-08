from abc import abstractmethod

from src.util.logger import Logger


class TelegramMenu:
    def __init__(self):
        Logger()
        self.menu_list = list()
        self.init_menu_list()
        self.add_receiver_handlers()

    @abstractmethod
    def init_menu_list(self):
        pass

    def add_receiver_handlers(self):
        if not Logger.log_telegram:
            return
        for menu_name, callback_func in self.menu_list:
            Logger.log_telegram.add_receiver_handler(menu_name=menu_name, callback_func=callback_func)

    def menu_callback(self, _, callback_context):
        try:
            msgs = list()
            for handler in callback_context.dispatcher.handlers[0]:
                menu_id = handler.command[1]
                menu_name = handler.command[0]
                msgs.append(f'{menu_id}. {menu_name}')
            Logger.write_to_bot('\n'.join(msgs))
        except Exception as e:
            Logger.write_error(e)
