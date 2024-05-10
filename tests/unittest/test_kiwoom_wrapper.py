import time

from src.kiwoom.buy_order_request import BuyOrderRequest
from src.kiwoom.kiwoom_chejan_service import KiwoomChejanService
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

    def test_get_orderbook(self):
        stock_code = '005930'
        stock_name = '삼성전자'
        orderbook_dict = self.kiwoom_wrapper.get_orderbook(stock_code)
        self.assertEqual(orderbook_dict['종목코드'], stock_code)
        self.assertEqual(orderbook_dict['종목명'], stock_name)

        if Helper.is_time_between('084001', '152000'):
            self.assertTrue(-30 <= float(orderbook_dict['등락률']) <= 30)
            self.assertTrue(int(orderbook_dict['매도1호가잔량']) > 0)
            self.assertTrue(int(orderbook_dict['매수1호가']) > 0)
            self.assertTrue(int(orderbook_dict['매수1호가잔량']) > 0)

    def test_get_buy_order_request(self):
        if Helper.is_time_between('084001', '085900'):
            stock_code = '005930'
            quantity = 1

            # 시장가 매수
            self.kiwoom_wrapper.request_market_buy_order(stock_code, quantity)
            time.sleep(0.25)

            # 매수 주문 요청을 조회 (장전 동시호가 시간이므로 체결이 안되는 상태임)
            df = self.kiwoom_wrapper.get_buy_order_request(stock_code)
            df = df[df['주문구분'] == '+매수']
            order_dict = df.iloc[0]
            self.assertEqual(order_dict['종목코드'], stock_code)
            self.assertEqual(int(order_dict['주문수량']), quantity)
            self.assertEqual(int(order_dict['체결량']), 0)
            order_no = order_dict['주문번호']
            time.sleep(0.25)

            # 주문취소
            self.kiwoom_wrapper.cancel_buy_order(stock_code, order_no)
            time.sleep(0.25)

            # 주문취소 확인
            df = self.kiwoom_wrapper.get_buy_order_request(stock_code)
            df = df[df['원주문번호'] == order_no]
            order_dict = df.iloc[0]
            self.assertEqual(order_dict['종목코드'], stock_code)
            self.assertEqual(order_dict['주문구분'], '매수취소')
            time.sleep(0.25)

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

            # 시장가 매도
            ret = self.kiwoom_wrapper.request_market_sell_order(stock_code, quantity)
            self.assertEqual(ret, 0)

    def test_chejan(self):
        kiwoom_chejan_service = KiwoomChejanService(self.kiwoom_wrapper, callback_chejan)
        kiwoom_chejan_service.start_service()
        time.sleep(100)
        kiwoom_chejan_service.stop_service()

    def test_real_orderbook(self):
        stock_code = '429270'
        order_book_service = KiwoomRealOrderbookService(self.kiwoom_wrapper, stock_code, callback_orderbook)
        order_book_service.start_service()
        time.sleep(100)
        order_book_service.stop_service()

def callback_chejan(data):
    Logger.write(data)

def callback_orderbook(stock_code, data):
    order_book = Orderbook(stock_code, data)
    Logger.write(order_book.is_ceiling_locked_safely())
