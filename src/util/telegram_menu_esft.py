from src.config_esft import ConfigEsft
from src.util.logger import Logger
from src.util.telegram_menu import TelegramMenu


class TelegramMenuEsft(TelegramMenu):
    def __init__(self):
        super().__init__()

    def init_menu_list(self):
        self.menu_list = [
            ('menu', self.menu_callback),
            ('set_top_1_stock_code', self.set_top_1_stock_code_callback),
            ('set_split_n', self.set_split_n_callback),
            ('block_stock_code', self.block_stock_code_callback),
            ('set_ceiling_breakaway_amount_billion', self.set_ceiling_breakaway_amount_billion_callback),
        ]

    def notify_service_created(self):
        Logger.write('서비스 시작')

    def block_stock_code_callback(self, _, callback_context):
        try:
            stock_code = callback_context.args[0]
            ConfigEsft.block_stock_codes.append(stock_code)
            Logger.write(f'block_stock_code에 종목 추가 - {stock_code}',
                         write_to_bot=True)
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
            Logger.write(f'top_1 종목코드 강제 지정 - {ConfigEsft.top_1_stock_code}',
                         write_to_bot=True)
        except Exception as e:
            Logger.write_error(e)

    def set_split_n_callback(self, _, callback_context):
        try:
            split_n = int(callback_context.args[0])
            ConfigEsft.split_n = split_n
        except Exception as e:
            ConfigEsft.split_n = 0
            Logger.write_error(e)
        Logger.write(f'분할 매수 횟수 강제 지정 - {ConfigEsft.split_n}',
                     write_to_bot=True)

    def set_ceiling_breakaway_amount_billion_callback(self, _, callback_context):
        try:
            ceiling_breakaway_amount_billion = float(callback_context.args[0])
            ConfigEsft.ceiling_breakaway_amount = ceiling_breakaway_amount_billion * 100_000_000
        except Exception as e:
            Logger.write_error(e)
        Logger.write(f'상한가 이탈 금액 설정 - {ConfigEsft.ceiling_breakaway_amount/100_000_000:.1f}억',
                     write_to_bot=True)

