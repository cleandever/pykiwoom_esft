import time

from src.config_esft import ConfigEsft
from src.kiwoom.chejan import Chejan
from src.kiwoom.expected_transaction_rate_top import ExpectedTransactionRateTop
from src.kiwoom.kiwoom_chejan_service import KiwoomChejanService
from src.kiwoom.kiwoom_real_orderbook_service import KiwoomRealOrderbookService
from src.kiwoom.orderbook import Orderbook
from src.util.helper import Helper
from src.kiwoom.kiwoom_wrapper import KiwoomWrapper
from src.util.logger import Logger


# 총 체결 수량
total_chejan_quantity = 0


def init_log():
    Logger.log_filename = Helper.get_init_log_filename(log_dir='../log/')
    Logger.write('')


def wait_until_market_open():
    while Helper.is_now_time_under('084000'):
        time.sleep(2)


def create_kiwoom_wrapper_and_login():
    kiwoom_wrapper = KiwoomWrapper(acc_no=ConfigEsft.acc_no)
    kiwoom_wrapper.login()
    return kiwoom_wrapper


def refresh_top_1_until_0902(expected_trans_rate_top):
    top_1 = {'stock_code': '',
             'price': 0,
             'split_n': 1}

    while Helper.is_now_time_under('090155'):
        expected_trans_rate_top.query()
        top_1 = expected_trans_rate_top.pick_top_1_to_buy()
        time.sleep(2)
    return top_1


def buy(kiwoom_wrapper, stock_code, price, split_n):
    # 증거금율을 적용한 최대매수가능수량 조회
    max_buy_quantity = kiwoom_wrapper.get_max_buy_quantity(stock_code, price)

    # 한 주문당 매수할 수량
    quantity_per_order = max_buy_quantity // split_n

    for _ in range(split_n):
        if quantity_per_order < 100:
            Logger.write('주문당 주문 수량이 100주 이하인 경우 예외가 발생하므로 프로그램 강제 종료')
            exit(1)
        kiwoom_wrapper.request_market_buy_order(stock_code, quantity_per_order)
        time.sleep(0.3)


def callback_orderbook(kiwoom_wrapper, stock_code, order_book_raw):
    order_book = Orderbook(stock_code, order_book_raw)
    if not order_book.is_ceiling_locked_safely():
        kiwoom_wrapper.request_market_sell_order(stock_code, total_chejan_quantity)
        #TODO: 보유한 주식 재확인 후 전량 매도
        exit(1)


def callback_chejan(kiwoom_wrapper, chejan_raw):
    global total_chejan_quantity
    Logger.write(chejan_raw)

    chejan = Chejan(chejan_raw)
    if chejan.is_chejan():
        chejan.parse_chejan()
        Logger.write(chejan.to_string())
        if chejan.chejan_quantity == 100:
            total_chejan_quantity += chejan.chejan_quantity
            kiwoom_wrapper.cancel_buy_order(chejan.stock_code, chejan.order_no)
            time.sleep(0.25)


def main():
    init_log()
    wait_until_market_open()

    kiwoom_wrapper = create_kiwoom_wrapper_and_login()
    expected_trans_rate_top = ExpectedTransactionRateTop(kiwoom_wrapper)
    top_1 = refresh_top_1_until_0902(expected_trans_rate_top)

    # 매수 대상 종목 확인
    stock_code, price, split_n = top_1['stock_code'], top_1['price'], top_1['split_n']

    # 매수 대상 종목코드 정보가 없다면 프로그램 종료
    if not stock_code:
        exit(1)

    # 실시간 호가
    order_book_service = KiwoomRealOrderbookService(kiwoom_wrapper, stock_code, callback_orderbook)
    order_book_service.start_service()

    # 실시간 체결
    chejan_service = KiwoomChejanService(kiwoom_wrapper, callback_chejan)
    chejan_service.start_service()

    # 분할 매수
    buy(kiwoom_wrapper, stock_code, price, split_n)

    while Helper.is_now_time_under('153000'):
        time.sleep(1)

    order_book_service.stop_service()
    chejan_service.stop_service()


if __name__ == "__main__":
    main()
