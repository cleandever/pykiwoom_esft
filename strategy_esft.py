import datetime
import threading
import time

from src.config_esft import ConfigEsft
from src.kiwoom.chejan import Chejan
from src.kiwoom.expected_transaction_rate_top import ExpectedTransactionRateTop
from src.kiwoom.kiwoom_chejan_service import KiwoomChejanService
from src.kiwoom.kiwoom_real_orderbook_service import KiwoomRealOrderbookService
from src.kiwoom.kiwoom_wrapper import KiwoomWrapper
from src.kiwoom.orderbook import Orderbook
from src.util.helper import Helper
from src.util.logger import Logger
from src.util.telegram_menu_esft import TelegramMenuEsft

# 총 체결 수량
total_chejan_quantity = 0

# 매수한 종목 코드
bought_stock_code = ''


def init_log():
    Logger.log_filename = Helper.get_init_log_filename(log_dir='./log/')
    Logger.init_telegram(ConfigEsft.telegram_chat_id, ConfigEsft.telegram_token)
    Logger.write('')


def wait_until_market_open():
    Logger.write('장 시작 대기 (~08:40)')
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
        time.sleep(3)
    return top_1


def buy(kiwoom_wrapper, stock_code, price, split_n):
    # 주문한 종목 코드를 저장
    global bought_stock_code
    bought_stock_code = stock_code

    # 증거금율을 적용한 최대매수가능수량 조회
    max_buy_quantity = kiwoom_wrapper.get_max_buy_quantity(stock_code, price)

    # 한 주문당 매수할 수량
    quantity_per_order = max_buy_quantity // split_n

    Logger.write(f'분할 매수 횟수 : {split_n}, '
                 f'매수 당 수량 : {quantity_per_order}, '
                 f'매수 당 금액 : {(quantity_per_order*price)//10_000}만원')

    for _ in range(split_n):
        if quantity_per_order < 100:
            Logger.write('주문당 주문 수량이 100주 이하인 경우 예외가 발생하므로 프로그램 강제 종료', write_to_bot=True)
            exit(1)
        kiwoom_wrapper.request_market_buy_order(stock_code, quantity_per_order)
        time.sleep(0.3)


def callback_orderbook(kiwoom_wrapper, stock_code, order_book_raw):
    order_book = Orderbook(stock_code, order_book_raw)
    if not order_book.is_ceiling_locked_safely():
        kiwoom_wrapper.request_market_sell_order(stock_code, total_chejan_quantity)
        time.sleep(1)
        # TODO: 보유한 주식 재확인 후 전량 매도
        Helper.terminate_current_process()


def callback_chejan(kiwoom_wrapper, chejan_raw):
    global total_chejan_quantity
    global bought_stock_code
    Logger.write(chejan_raw)

    chejan = Chejan(chejan_raw)
    if chejan.is_chejan():
        chejan.parse_chejan()

        if bought_stock_code != chejan.stock_code:
            Logger.write(f'쩜상 프로그램에서 매수한 체결 정보가 아니므로 무시 - '
                         f'종목코드 : {chejan.stock_code}')
            return

        Logger.write(chejan.to_string(), write_to_bot=True)
        if chejan.chejan_quantity == 100:
            total_chejan_quantity += chejan.chejan_quantity
            kiwoom_wrapper.cancel_buy_order(chejan.stock_code, chejan.order_no)
            time.sleep(0.25)


def validate_kiwoom_api_status(kiwoom_wrapper):
    # 시장가 주문
    # 주문 취소
    pass


def get_seconds_until_target_time(target_hour=9, target_minute=3):
    now = datetime.datetime.now()
    target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)

    time_diff = int((target_time - now).total_seconds())
    return time_diff if time_diff > 0 else 0


def check_and_terminate_if_no_position():
    seconds_to_wait = get_seconds_until_target_time(target_hour=9, target_minute=3)
    time.sleep(seconds_to_wait)

    global bought_stock_code
    if not bought_stock_code:
        Logger.write('매수한 종목이 없으므로 프로세스 강제 종료')
        Helper.terminate_current_process()


def main():
    init_log()
    threading.Thread(target=check_and_terminate_if_no_position).start()
    wait_until_market_open()

    telegram_menu = TelegramMenuEsft()
    telegram_menu.notify_service_created()

    kiwoom_wrapper = create_kiwoom_wrapper_and_login()
    validate_kiwoom_api_status(kiwoom_wrapper)

    expected_trans_rate_top = ExpectedTransactionRateTop(kiwoom_wrapper)
    top_1 = refresh_top_1_until_0902(expected_trans_rate_top)

    # 매수 대상 종목 확인
    stock_code, price, split_n = top_1['stock_code'], top_1['price'], top_1['split_n']

    # 강제 수동 지정
    #stock_code = ''
    #price = 0
    #split_n = 0

    # 매수 대상 종목코드 정보가 없다면 프로그램 종료
    if not stock_code:
        Helper.terminate_current_process()

    Logger.write(f'매수 대상 선정 완료 - 종목코드 : {stock_code}, '
                 f'가격 : {price}, '
                 f'분할 매수 : {split_n}')

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
