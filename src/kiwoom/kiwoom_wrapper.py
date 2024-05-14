import time

from src.kiwoom.orderbook import order_book_fid
from src.pykiwoom.manager import KiwoomManager
from src.util.logger import Logger


class OrderType:
    신규매수 = 1
    신규매도 = 2
    매수취소 = 3
    매도취소 = 4
    매수정정 = 5
    매도정정 = 6


class HogaType:
    지정가 = '00'
    시장가 = '03'
    NONE = ''


class KiwoomWrapper:
    def __init__(self, acc_no):
        self.km = None
        self.acc_no = acc_no
        self.method_screen_no = '0100'
        self.tr_screen_no = '0200'
        self.real_screen_no = '0300'

    def login(self):
        # 객체 생성하면서 동시에 백그라운드로 로그인인 발생함
        Logger.write('키움 로그인 시도')
        self.km = KiwoomManager()
        self.wait_until_login_completed()
        Logger.write('키움 로그인 완료')

    def wait_until_login_completed(self):
        while not self.is_connected():
            time.sleep(1)

    def is_connected(self):
        self.km.put_method(("IsConnected", ''))
        connected = self.km.get_method()
        return connected

    # 예상체결등락률상위
    def get_expected_transaction_rate_top(self):
        """
	    시장구분 = 000:전체, 001:코스피, 101:코스닥
	    정렬구분 = 1:상승률, 2:상승폭, 3:보합, 4:하락률,5:하락폭, 6, 체결량, 7:상한, 8:하한
	    거래량조건 = 0:전체조회, 1;천주이상, 3:3천주이상, 5:5천주이상, 10:만주이상, 50:5만주이상, 100:10만주이상
	    종목조건 = 0:전체조회, 1:관리종목제외, 3:우선주제외, 4:관리종목,우선주제외, 5:증100제외, 6:증100만보기,
	               7:증40만보기, 8:증30만보기, 9:증20만보기, 11:정리매매종목제외, 12:증50만보기, 13:증60만보기,
	               14:ETF제외, 15:스팩제외, 16:ETF+ETN제외
	    신용조건 = 0:전체조회, 1:신용융자A군, 2:신용융자B군, 3:신용융자C군, 4:신용융자D군, 5:신용한도초과제외, 8:신용대주, 9:신용융자전체
	    가격조건 = 0:전체조회, 1:1천원미만, 2:1천원~2천원, 3:2천원~
        """
        tr_cmd = {
            'rqname': "opt10029",
            'trcode': 'opt10029',
            'next': '0',
            'screen': self.tr_screen_no,
            'input': {
                "시장구분": "000",
                "정렬구분": 1,
                "거래량조건": "10",
                "종목조건": "16",
                "신용조건": "0",
                "가격조건": "0"
            },
            'output': ['종목코드', '종목명', '등락률', '예상체결가', '예상체결량', '매도잔량', '매수잔량']
        }
        self.km.put_tr(tr_cmd)
        df, remain = self.km.get_tr()
        return df

    # 시세표성정보요청
    def get_orderbook(self, stock_code):
        tr_cmd = {
            'rqname': "opt10007",
            'trcode': 'opt10007',
            'next': '0',
            'screen': self.tr_screen_no,
            'input': {
                "종목코드": stock_code
            },
            'output': ['종목코드', '종목명', '등락률', '매도1호가잔량',
                       '매수1호가', '매수1호가잔량', '상한가']
        }
        self.km.put_tr(tr_cmd)
        df, remain = self.km.get_tr()
        return df.iloc[0]

    def get_max_buy_quantity(self, stock_code, price):
        output = ['적용증거금율']

        margin_list = [20, 30, 40, 50, 60, 100]
        for margin in margin_list:
            output.append(f'증거금{margin}주문가능수량')

        tr_cmd = {
            'rqname': "opw00011",
            'trcode': 'opw00011',
            'next': '0',
            'screen': self.tr_screen_no,
            'input': {
                '계좌번호': self.acc_no,
                '비밀번호': "",
                '비밀번호입력매체구분': "00",
                '종목번호': stock_code,
                '매수가격': str(price),
            },
            'output': output
        }
        self.km.put_tr(tr_cmd)
        df, remain = self.km.get_tr()
        row = df.iloc[0]

        applied_margin_rate = row['적용증거금율'].strip('%')
        max_buy_quantity = int(row[f'증거금{applied_margin_rate}주문가능수량'])
        Logger.write(f'증거금 적용 최대주문가능수량 - '
                     f'종목코드 : {stock_code} : '
                     f'최대주문가능수량 : {max_buy_quantity}')
        return max_buy_quantity

    # 시장가 매수 주문
    def request_market_buy_order(self, stock_code, quantity):
        Logger.write(f'시장가 매수 주문 요청 - 종목코드 : {stock_code}, 수량 : {quantity}')
        price = 0
        order_no = ''
        self.km.put_method(("SendOrder", "시장가매수", self.method_screen_no, self.acc_no,
                            OrderType.신규매수, stock_code, quantity, price, HogaType.시장가, order_no))
        ret = self.km.get_method()
        Logger.write(f'시장가 매수 주문 완료 - 종목코드 : {stock_code}, 수량 : {quantity}, 반환값 : {ret}')
        return ret

    # 시장가 매도 주문
    def request_market_sell_order(self, stock_code, quantity):
        Logger.write(f'시장가 매도 주문 요청 - 종목코드 : {stock_code}, 수량 : {quantity}')
        price = 0
        order_no = ''
        self.km.put_method(("SendOrder", "시장가매도", self.method_screen_no, self.acc_no,
                            OrderType.신규매도, stock_code, quantity, price, HogaType.시장가, order_no))
        ret = self.km.get_method()
        Logger.write(f'시장가 매도 주문 완료 - 종목코드 : {stock_code}, 수량 : {quantity}, 반환값 : {ret}')
        return ret

    # (전체) 매수 주문 취소
    def cancel_buy_order(self, stock_code, order_no):
        Logger.write(f'매수 주문 취소 요청 - 종목코드 : {stock_code}, 주문번호 : {order_no}')
        price = 0
        quantity = 0
        self.km.put_method(("SendOrder", "매수주문취소", self.method_screen_no, self.acc_no,
                            OrderType.매수취소, stock_code, quantity, price, HogaType.NONE, order_no))
        ret = self.km.get_method()
        Logger.write(f'매수 주문 취소 완료 - 종목코드 : {stock_code}, 주문번호 : {order_no}, 반환값 : {ret}')

    def register_real(self, stock_code):
        fid_list = list(order_book_fid.values())
        real_cmd = {
            'func_name': "SetRealReg",
            'real_type': '주식호가잔량',
            'screen': self.real_screen_no,
            'code_list': [stock_code],
            'fid_list': fid_list,
            "opt_type": 0
        }
        self.km.put_real(real_cmd)

    def unregister_real(self):
        self.km.put_method(("DisconnectRealData", self.real_screen_no))

