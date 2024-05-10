from src.config_esft import ConfigEsft
from src.util.logger import Logger


class ExpectedTransactionRateTop:
    def __init__(self, kiwoom_wrapper):
        self.kiwoom_wrapper = kiwoom_wrapper
        self.df = None

    def query(self):
        self.df = self.kiwoom_wrapper.get_expected_transaction_rate_top()

    def pick_top_1_to_buy(self):
        top_1_stock_code = ''
        top_1_stock_name = ''
        top_1_expected_price = 0
        top_1_buy_amount = 0
        top_1_split_n = 1

        for i, row in self.df.iterrows():
            stock_code = row['종목코드']
            stock_name = row['종목명']
            rate = float(row['등락률'])
            expected_price = int(row['예상체결가'])
            expected_trading_quantity = int(row['예상체결량'])
            sell_quantity = int(row['매도잔량'])
            buy_quantity = int(row['매수잔량'])
            buy_amount = expected_price * buy_quantity
            expected_trading_amount = expected_price * expected_trading_quantity
            split_n = max(expected_trading_amount // 100_000_000, 1)
            split_n = min(split_n, 9)

            if rate < 29.5 or sell_quantity > 0:
                continue

            if buy_amount > top_1_buy_amount:
                top_1_stock_code = stock_code
                top_1_stock_name = stock_name
                top_1_expected_price = expected_price
                top_1_buy_amount = buy_amount
                top_1_split_n = split_n

            Logger.write(f'종목코드 : {stock_code}, '
                         f'종목명 : {stock_name}, '
                         f'등락률 : {rate}, '
                         f'예상체결가 : {expected_price}, '
                         f'예상체결량 : {expected_trading_quantity}, '
                         f'예상거래대금 : {expected_trading_amount//100_000_000}억, '
                         f'분할매수 횟수 : {split_n}, '
                         f'매도잔량 : {sell_quantity}, '
                         f'매수잔량 : {buy_quantity}, '
                         f'매수잔량금액 : {buy_amount//100_000_000}억')

        # 최우선매수잔량금액의 최소 금액 조건 확인
        if top_1_buy_amount < ConfigEsft.buy_condition_buy_amount1_threshold:
            # clear
            top_1_stock_code = ''
            top_1_stock_name = ''
            top_1_expected_price = 0
            top_1_split_n = 1

        Logger.write(f'매수 후보 - 종목코드 : {top_1_stock_code}({top_1_stock_name})')
        top_1 = {'stock_code': top_1_stock_code,
                 'price': top_1_expected_price,
                 'split_n': top_1_split_n}
        return top_1
