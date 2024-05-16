import unittest

from src.kiwoom.orderbook import Orderbook, order_book_fid


def create_dummy_order_book_raw():
    order_book_raw = dict()
    #order_book_raw['등락률'] = '+29.8'
    order_book_raw[order_book_fid['매도호가1']] = '0'
    order_book_raw[order_book_fid['매도호가수량1']] = '0'
    order_book_raw[order_book_fid['매수호가1']] = '50000'
    order_book_raw[order_book_fid['매수호가수량1']] = '10000000'
    return order_book_raw


class TestOrderbook(unittest.TestCase):
    def test_is_ceiling_locked_safely_on_true(self):
        stock_code = '005930'
        order_book_raw = create_dummy_order_book_raw()
        # 상한가 잠겨있는 수량
        order_book_raw[order_book_fid['매수호가수량1']] = '10000000'

        order_book = Orderbook(stock_code, order_book_raw)
        self.assertTrue(order_book.is_ceiling_locked_safely())

    def test_is_ceiling_locked_safely_on_false(self):
        stock_code = '005930'
        order_book_raw = create_dummy_order_book_raw()
        # 상한가 풀려있는 수량
        order_book_raw[order_book_fid['매수호가수량1']] = '10000'
        order_book = Orderbook(stock_code, order_book_raw)
        self.assertFalse(order_book.is_ceiling_locked_safely())
