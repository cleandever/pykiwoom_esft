import unittest

from src.kiwoom.orderbook import Orderbook
from tests.unittest.kiwoom_test import KiwoomTest


class TestOrderbook(KiwoomTest):
    def setUp(self):
        self.stock_code = '005930'
        self.order_book = Orderbook(self.kiwoom_wrapper, self.stock_code)

    def test_query(self):
        self.order_book.query()
        self.assertTrue(len(self.order_book.order_book_raw) > 0)

    def test_is_ceiling_locked_safely(self):
        self.order_book.query()
        self.assertFalse(self.order_book.is_ceiling_locked_safely())

        # 데이터 임의 조작 (상한가 잠김 조건)
        order_book_raw = self.order_book.order_book_raw
        order_book_raw['등락률'] = '+29.8'
        order_book_raw['매도1호가잔량'] = '0'
        order_book_raw['매수1호가'] = '50000'
        order_book_raw['매수1호가잔량'] = '10000000'
        self.assertTrue(self.order_book.is_ceiling_locked_safely())

    @unittest.skip('현재 상한가에 잠긴 경우만 테스트 수행')
    def test_real_stock(self):
        # 현재 상한가에 잠긴 종목을 테스트 수행
        stock_code = '309960'
        order_book = Orderbook(self.kiwoom_wrapper, stock_code)
        order_book.query()
        self.assertTrue(order_book.is_ceiling_locked_safely())

