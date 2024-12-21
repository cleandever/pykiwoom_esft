from src.config_esft import ConfigEsft
from src.util.logger import Logger
from src.util.telegram_menu import TelegramMenu


class TelegramMenuEsft(TelegramMenu):
    def __init__(self):
        super().__init__()

    def init_menu_list(self):
        self.menu_list = [
            ('menu', self.menu_callback),
            ('set_top_1', self.set_top_1_callback),
            ('clear_top_1', self.clear_top_1_callback),
            ('block_stock_code', self.block_stock_code_callback),
            ('set_ceiling_breakaway_amount', self.set_ceiling_breakaway_amount_billion_callback)
        ]

    def notify_service_created(self):
        Logger.write('서비스 시작')

    def set_top_1_callback(self, _, callback_context):
        try:
            args = callback_context.args[0].split(',')
            ConfigEsft.top_1_stock_code = args[0].strip()
            ConfigEsft.price = int(args[1].strip())
            ConfigEsft.split_n = int(args[2].strip())
            Logger.write(f'매수 종목 강제 지정 - '
                         f'종목코드 : {ConfigEsft.top_1_stock_code}, '
                         f'가격 : {ConfigEsft.price}, '
                         f'분할 매수 횟수 : {ConfigEsft.split_n}', write_to_bot=True)
        except Exception as e:
            Logger.write_error(e)
            Logger.write('종목코드,가격,분할매수횟수 형식으로 입력하세요!', write_to_bot=True)

    def clear_top_1_callback(self, _, callback_context):
        try:
            ConfigEsft.top_1_stock_code = ''
            ConfigEsft.price = 0
            ConfigEsft.split_n = 0
            Logger.write(f'매수 종목 clear - '
                         f'종목코드 : {ConfigEsft.top_1_stock_code}, '
                         f'가격 : {ConfigEsft.price}, '
                         f'분할 매수 횟수 : {ConfigEsft.split_n}', write_to_bot=True)
        except Exception as e:
            Logger.write_error(e)

    def block_stock_code_callback(self, _, callback_context):
        try:
            stock_code = callback_context.args[0]
            ConfigEsft.block_stock_codes.append(stock_code)
            Logger.write(f'block_stock_code에 종목 추가 - {stock_code}',
                         write_to_bot=True)
        except Exception as e:
            Logger.write_error(e)

    def set_ceiling_breakaway_amount_billion_callback(self, _, callback_context):
        try:
            ceiling_breakaway_amount_billion = float(callback_context.args[0])
            ConfigEsft.ceiling_breakaway_amount = ceiling_breakaway_amount_billion * 100_000_000
        except Exception as e:
            Logger.write_error(e)
        Logger.write(f'상한가 이탈 금액 설정 - {ConfigEsft.ceiling_breakaway_amount/100_000_000:.1f}억',
                     write_to_bot=True)

