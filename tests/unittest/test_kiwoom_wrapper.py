import time

from src.kiwoom.chejan import Chejan
from src.kiwoom.kiwoom_chejan_service import KiwoomChejanService
from src.kiwoom.kiwoom_real_market_open_time_service import KiwoomRealMarketOpenTimeService
from src.kiwoom.kiwoom_real_orderbook_service import KiwoomRealOrderbookService
from src.kiwoom.orderbook import Orderbook
from src.util.helper import Helper
from src.util.logger import Logger
from tests.unittest.kiwoom_test import KiwoomTest


class TestKiwoomWrapper(KiwoomTest):
    def setUp(self):
        time.sleep(0.25)

    def test_get_expected_transaction_rate_top(self):
        df = self.kiwoom_wrapper.get_expected_transaction_rate_top()
        if Helper.is_time_between('084000', '152000'):
            self.assertTrue(len(df.index) > 0)
            self.assertTrue(df.iloc[0]['종목코드'])

    def test_get_margin_rate(self):
        stock_code = '005930'
        margin_rate = self.kiwoom_wrapper.get_margin_rate(stock_code)
        self.assertTrue(margin_rate <= 100)

        # from cache
        margin_rate = self.kiwoom_wrapper.get_margin_rate(stock_code)
        self.assertTrue(margin_rate <= 100)

    def test_get_max_buy_quantity(self):
        stock_code = '005930'
        orderbook_dict = self.kiwoom_wrapper.get_orderbook(stock_code)
        upper_price = int(orderbook_dict['상한가'])
        time.sleep(0.25)

        max_buy_quantity = self.kiwoom_wrapper.get_max_buy_quantity(stock_code, upper_price)
        self.assertTrue(max_buy_quantity > 0)

    def test_real_buy_and_sell_order(self):
        if Helper.is_time_between('090000', '152000'):
            # SK증권
            stock_code = '001510'
            quantity = 1

            # 시장가 매수
            ret = self.kiwoom_wrapper.request_market_buy_order(stock_code, quantity)
            self.assertEqual(ret, 0)

            # 매수가 체결되도록 잠시 대기
            time.sleep(1)

            # 매수 됐으므로 보유수량 1
            holding_quantity = self.kiwoom_wrapper.get_stock_holding_quantity(stock_code)
            self.assertEqual(holding_quantity, quantity)

            # 시장가 매도
            ret = self.kiwoom_wrapper.request_market_sell_order(stock_code, quantity)
            self.assertEqual(ret, 0)

            # 매도 했으므로 보유수량 0
            holding_quantity = self.kiwoom_wrapper.get_stock_holding_quantity(stock_code)
            self.assertEqual(holding_quantity, 0)


    def test_real_chejan(self):
        kiwoom_chejan_service = KiwoomChejanService(self.kiwoom_wrapper, callback_chejan)
        kiwoom_chejan_service.start_service()
        time.sleep(3)
        kiwoom_chejan_service.stop_service()

    def test_real_orderbook(self):
        stock_code = '003350'
        order_book_service = KiwoomRealOrderbookService(self.kiwoom_wrapper, stock_code, callback_orderbook)
        order_book_service.start_service()
        time.sleep(3)
        order_book_service.stop_service()

    def test_market_open_time(self):
        market_open_time_service = KiwoomRealMarketOpenTimeService(self.kiwoom_wrapper, callback_market_open_time)
        market_open_time_service.start_service()
        time.sleep(3)
        market_open_time_service.stop_service()


def callback_chejan(kiwoom_wrapper, chejan_raw):
    Logger.write(chejan_raw)

    chejan = Chejan(chejan_raw)
    if chejan.is_chejan():
        chejan.parse_chejan()
        Logger.write(chejan.to_string())


def callback_orderbook(kiwoom_wrapper, stock_code, order_book_raw):
    order_book = Orderbook(stock_code, order_book_raw)
    Logger.write(order_book.is_ceiling_locked_safely())


def callback_market_open_time(market_open_time_raw):
    Logger.write(market_open_time_raw)