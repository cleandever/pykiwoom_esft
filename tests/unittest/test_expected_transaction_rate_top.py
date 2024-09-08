import unittest
from unittest.mock import Mock, patch
import pandas as pd

from src.config_esft import ConfigEsft
from src.kiwoom.expected_transaction_rate_top import ExpectedTransactionRateTop


class TestExpectedTransactionRateTop(unittest.TestCase):
    def setUp(self):
        self.mock_kiwoom_wrapper = Mock()
        self.etr_top = ExpectedTransactionRateTop(self.mock_kiwoom_wrapper)

    def test_query(self):
        mock_df = pd.DataFrame({'test': [1, 2, 3]})
        self.mock_kiwoom_wrapper.get_expected_transaction_rate_top.return_value = mock_df
        self.etr_top.query()
        self.assertTrue(self.etr_top.df.equals(mock_df))

    @patch('src.util.logger.Logger')
    @patch('src.config_esft.ConfigEsft')
    def test_pick_top_1_to_buy(self, mock_config, mock_logger):
        mock_config.buy_condition_buy_amount1_threshold = 100_000_000_000
        mock_config.top_1_stock_code = None
        mock_config.block_stock_codes = ['123456']

        test_data = {
            '종목코드': ['000001', '000002', '123456', '000003'],
            '종목명': ['Stock1', 'Stock2', 'Blocked', 'Stock3'],
            '등락률': ['29.9', '30.0', '29.8', '29.7'],
            '예상체결가': [1000, 2000, 3000, 4000],
            '예상체결량': [1000, 2000, 3000, 4000],
            '매도잔량': [0, 0, 100, 0],
            '매수잔량': [10000, 20000, 30000, 400000000]
        }
        self.etr_top.df = pd.DataFrame(test_data)

        result = self.etr_top.pick_top_1_to_buy()

        self.assertEqual(result['stock_code'], '000003')
        self.assertEqual(result['price'], 4000)

    def test_get_split_n(self):
        result = self.etr_top.get_split_n(10000000000)
        self.assertEqual(result, 9)

        ConfigEsft.split_n = 3
        result = self.etr_top.get_split_n(10000000000)
        self.assertEqual(result, 3)

        ConfigEsft.split_n = 0
        result = self.etr_top.get_split_n(10000000000)
        self.assertEqual(result, 9)

    def test_is_blocked_stock_code(self):
        ConfigEsft.block_stock_codes = ['123456', '789012']
        self.assertTrue(self.etr_top._is_blocked_stock_code('123456'))
        self.assertFalse(self.etr_top._is_blocked_stock_code('000001'))
