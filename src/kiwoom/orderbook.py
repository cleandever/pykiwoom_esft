from src.config_esft import ConfigEsft
from src.util.logger import Logger

order_book_fid = {
    '매도호가1': '41',
    '매도호가수량1': '61',
    '매수호가1': '51',
    '매수호가수량1': '71',
}


class Orderbook:
    def __init__(self, stock_code, order_book_raw):
        self.stock_code = stock_code
        self.order_book_raw = order_book_raw

    def is_ceiling_locked_safely(self):
        sell_balance_quantity1 = int(self.order_book_raw[order_book_fid['매도호가수량1']])
        buy_amount = int(self.order_book_raw[order_book_fid['매수호가1']]) * int(self.order_book_raw[order_book_fid['매수호가수량1']])
        Logger.write(f'호가 기본 정보 - '
                     f'종목코드 : {self.stock_code}, '
                     f'매도호가수량1: {sell_balance_quantity1}, '
                     f'최우선매수잔량금액 : {buy_amount//100_000_000}억')

        if sell_balance_quantity1 > 0:
            return False

        if buy_amount < ConfigEsft.ceiling_breakaway_amount:
            return False

        return True
