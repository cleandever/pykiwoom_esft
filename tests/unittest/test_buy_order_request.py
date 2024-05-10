import unittest
from unittest.mock import patch

import pandas as pd
from pykiwoom.kiwoom import Kiwoom

from src.kiwoom.buy_order_request import BuyOrderRequest
from src.kiwoom.kiwoom_wrapper import KiwoomWrapper
from tests.unittest.kiwoom_test import KiwoomTest


class TestBuyOrderRequest(KiwoomTest):
    def setUp(self):
        self.stock_code = '005930'
        self.buy_order_req = BuyOrderRequest(self.kiwoom_wrapper, self.stock_code)

    def test_query(self):
        self.buy_order_req.query()
        self.assertIsNotNone(self.buy_order_req)

    def test_cancel_if_new_chejan_occur(self):
        # dummy 체결요청 응답 데이터 생성
        data = {
            # 주문구분, 체결량, 주문번호
            '0': ['+매수', '100', '0000111'],
            '1': ['매수취소', '0', '0000999'],
            '2': ['+매수', '100', '0000222'],
            '3': ['매수', '0', '0000333'],
        }
        df = pd.DataFrame.from_dict(data=data, orient='index', columns=['주문구분', '체결량', '주문번호'])

        with (patch.object(KiwoomWrapper, 'get_buy_order_request', return_value=df),
              patch.object(Kiwoom, 'SendOrder', return_value=0)):
            self.buy_order_req.query()
            total_chejan_quantity = self.buy_order_req.cancel_if_new_chejan_occur()
            self.assertEqual(total_chejan_quantity, 200)

    @unittest.skip('개별적인 테스트에서만 활성화')
    def test_real(self):
        stock_code = '309960'
        buy_order_req = BuyOrderRequest(self.kiwoom_wrapper, stock_code)
        buy_order_req.query()
        buy_order_req.cancel_if_new_chejan_occur()

