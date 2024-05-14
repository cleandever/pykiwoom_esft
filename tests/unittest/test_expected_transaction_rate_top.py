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

    def test_get_split_n(self):
        self.assertEqual(self.expected_trans_rate_top.get_split_n(50_000_000_000), 9)
        self.assertEqual(self.expected_trans_rate_top.get_split_n(120_000_000_000), 8)
        self.assertEqual(self.expected_trans_rate_top.get_split_n(190_000_000_000), 7)
        self.assertEqual(self.expected_trans_rate_top.get_split_n(220_000_000_000), 7)
        self.assertEqual(self.expected_trans_rate_top.get_split_n(280_000_000_000), 6)
        self.assertEqual(self.expected_trans_rate_top.get_split_n(530_000_000_000), 2)
        self.assertEqual(self.expected_trans_rate_top.get_split_n(610_000_000_000), 1)
        self.assertEqual(self.expected_trans_rate_top.get_split_n(910_000_000_000), 1)
