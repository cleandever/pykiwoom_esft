from src.config_esft import ConfigEsft
from src.util.company_wise import CompanyWise
from src.util.logger import Logger


class ExpectedTransactionRateTop:
    def __init__(self, kiwoom_wrapper):
        self.kiwoom_wrapper = kiwoom_wrapper
        self.df = None

    def query(self):
        self.df = self.kiwoom_wrapper.get_expected_transaction_rate_top()

    def pick_top_1_to_buy(self):
        top_1_stock_code = ''
        top_1_expected_price = 0
        top_1_buy_amount = 0
        top_1_buy_quantity_percent_on_floating_stock_count = 0
        top_1_split_n = 1

        candidate_stock_info = {}
        for i, row in self.df.iterrows():
            stock_code = row['종목코드']
            if self._is_blocked_stock_code(stock_code):
                Logger.write(f'blocked 종목 코드 skip - 종목코드 : {stock_code}')
                continue

            stock_name = row['종목명']
            rate = float(row['등락률'])
            expected_price = int(row['예상체결가'])
            expected_trading_quantity = int(row['예상체결량'])
            sell_quantity = int(row['매도잔량'])
            buy_quantity = int(row['매수잔량'])
            buy_amount = expected_price * buy_quantity
            expected_trading_amount = expected_price * expected_trading_quantity
            floating_stock_count = self._get_floating_stock_count(stock_code)

            # 유동주식수 획득에 실패한 경우 무조건 100% 강제 지정
            # 100% 강제 지정은 top 1 선택시 해당 조건을 안 보겠다는 의미
            buy_quantity_percent_on_floating_stock_count = (buy_quantity / floating_stock_count) * 100 \
                if floating_stock_count > 0 else 100

            split_n = self.get_split_n(buy_amount, expected_price, floating_stock_count)

            candidate_stock_info['stock_code'] = {
                'stock_name': stock_name,
                'price': expected_price,
                'split_n': split_n
            }

            # 등락률 폭
            if not (29.5 <= rate <= 30):
                continue

            # 매도잔량은 무조건 0임
            if sell_quantity > 0:
                continue

            if buy_amount > top_1_buy_amount:
                top_1_stock_code = stock_code
                top_1_expected_price = expected_price
                top_1_buy_amount = buy_amount
                top_1_buy_quantity_percent_on_floating_stock_count = buy_quantity_percent_on_floating_stock_count
                top_1_split_n = split_n

            Logger.write(f'종목코드 : {stock_code}, '
                         f'종목명 : {stock_name}, '
                         f'등락률 : {rate}%, '
                         f'예상체결가 : {expected_price}, '
                         f'예상체결량 : {expected_trading_quantity}, '
                         f'예상거래대금 : {expected_trading_amount//100_000_000}억, '
                         f'유통주식수 : {floating_stock_count}, '
                         f'최우선매수잔량비율 : {buy_quantity_percent_on_floating_stock_count:.1f}%, '
                         f'분할매수 횟수 : {split_n}, '
                         f'매도잔량 : {sell_quantity}, '
                         f'매수잔량 : {buy_quantity}, '
                         f'매수잔량금액 : {buy_amount//100_000_000}억')

        # 매수하기 위한 최우선매수잔량 최소 조건 확인
        if (top_1_buy_amount < ConfigEsft.buy_condition_buy_amount1_threshold and
                top_1_buy_quantity_percent_on_floating_stock_count < ConfigEsft.buy_condition_buy_qty_percent_on_floating_stock_count):
            # clear
            top_1_stock_code = ''
            top_1_expected_price = 0
            top_1_split_n = 1

        return self._get_top_1(top_1_stock_code, top_1_expected_price, top_1_split_n)

    def _get_top_1(self, top_1_stock_code, top_1_expected_price, top_1_split_n):
        if ConfigEsft.top_1_stock_code and ConfigEsft.price > 0 and ConfigEsft.split_n > 0:
            # 강제 수동 지정 (텔레그램)
            top_1 = {'stock_code': ConfigEsft.top_1_stock_code,
                     'price': ConfigEsft.price,
                     'split_n': ConfigEsft.split_n}
        else:
            top_1 = {'stock_code': top_1_stock_code,
                     'price': top_1_expected_price,
                     'split_n': top_1_split_n}
        Logger.write(f'매수 후보 - {top_1})')
        return top_1

    def get_split_n(self, buy_amount, expected_price=None, floating_stock_count=None):
        # 강제 설정된 분할 매수 횟수
        if ConfigEsft.split_n > 0:
            return ConfigEsft.split_n

        buy_amount_billion = buy_amount // 100_000_000

        # 3000억원 이하는 9방 매수 기준 추세선
        split_n = int(-0.002 * buy_amount_billion + 15)

        # 유통주식수가 굉장히 적으면 분할매수 횟수를 크게 줄임 (일반적으로 우선주)
        if floating_stock_count and floating_stock_count < 5_000_000:
            split_n = 1

        if buy_amount_billion > ConfigEsft.buy_condition_buy_amount1_threshold:
            # 증거금율이 100%가 아니면 분할 매수 횟수 1회 추가
            # caching된 데이터에서 계속 조회하게 되므로 API 조회 부하
            if self.kiwoom_wrapper.get_margin_rate() != 100:
                split_n += 1

        # 동전주 배분 물량이 많아서 배분 받을 확률이 굉장히 높음
        if expected_price and expected_price < 1_000:
            split_n = 9

        split_n = min(split_n, 9)
        split_n = max(split_n, 1)
        return split_n

    def _is_blocked_stock_code(self, stock_code):
        return stock_code in ConfigEsft.block_stock_codes

    def _get_floating_stock_count(self, stock_code):
        floating_stock_count = CompanyWise.get_floating_stock_count(stock_code)
        if floating_stock_count == 0:
            kiwoom_floating_stock_count = self.kiwoom_wrapper.get_floating_stock_count(stock_code)
            if kiwoom_floating_stock_count == 0:
                return self.kiwoom_wrapper.get_total_stock_count(stock_code)
        return floating_stock_count
