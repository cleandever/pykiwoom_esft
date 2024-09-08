from src.config_esft import ConfigEsft
from src.util.logger import Logger
from src.util.telegram_menu import TelegramMenu


class TelegramMenuEsft(TelegramMenu):
    def __init__(self, observer_esft):
        super().__init__()
        self.observer_esft = observer_esft

    def init_menu_list(self):
        self.menu_list = [
            ('menu', self.menu_callback),
            ('set_top_1_stock_code', self.set_top_1_stock_code_callback),
            ('set_split_n', self.set_split_n_callback),
            ('block_stock_code', self.block_stock_code_callback)
        ]

    def block_stock_code_callback(self, _, callback_context):
        try:
            stock_code = callback_context.args[0]
            ConfigEsft.block_stock_codes.append(stock_code)
            Logger.write(f'block_stock_code에 종목 추가 - {stock_code}')
        except Exception as e:
            Logger.write_error(e)

    def set_top_1_stock_code_callback(self, _, callback_context):
        try:
            if len(callback_context.args) == 0:
                # 아무것도 입력하지 않으면 초기화
                ConfigEsft.top_1_stock_code = ''
            else:
                stock_code = callback_context.args[0]
                ConfigEsft.top_1_stock_code = stock_code
            Logger.write(f'top_1 종목코드 강제 지정 - {ConfigEsft.top_1_stock_code}')
        except Exception as e:
            Logger.write_error(e)

    def set_split_n_callback(self, _, callback_context):
        try:
            split_n = callback_context.args[0]
            ConfigEsft.split_n = split_n
        except Exception as e:
            ConfigEsft.split_n = 0
            Logger.write_error(e)
        Logger.write(f'분할 매수 횟수 강제 지정 - {ConfigEsft.split_n}')
