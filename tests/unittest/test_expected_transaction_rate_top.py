from src.config_esft import ConfigEsft
from src.kiwoom.expected_transaction_rate_top import ExpectedTransactionRateTop
from tests.unittest.kiwoom_test import KiwoomTest


class TestExpectedTransactionRateTop(KiwoomTest):
    def setUp(self):
        self.expected_trans_rate_top = ExpectedTransactionRateTop(self.kiwoom_wrapper)

    def test_query(self):
        self.expected_trans_rate_top.query()
        self.assertTrue(len(self.expected_trans_rate_top.df) > 0)

    def test_pick_top_1_to_buy(self):
        self.expected_trans_rate_top.query()

        df = self.expected_trans_rate_top.df

        # 데이터 조작
        stock_code = df.iloc[0]['종목코드']
        df.iloc[0]['등락률'] = '+29.9'
        df.iloc[0]['예상체결가'] = '5000'
        df.iloc[0]['예상체결량'] = '100000'
        df.iloc[0]['매도잔량'] = '0'
        df.iloc[0]['매수잔량'] = '100000000'
        top_1 = self.expected_trans_rate_top.pick_top_1_to_buy()
        self.assertEqual(top_1['stock_code'], stock_code)

        # 매수 조건 금액을 굉장히 크게 높였을 때는 만족하는 종목 코드가 없어야함
        ConfigEsft.buy_condition_buy_amount1_threshold = 999_999_999_999_999
        top_1 = self.expected_trans_rate_top.pick_top_1_to_buy()
        self.assertEqual(top_1['stock_code'], '')
