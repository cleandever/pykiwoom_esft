import time


class BuyOrderRequest:
    def __init__(self, kiwoom_wrapper, stock_code):
        self.kiwoom_wrapper = kiwoom_wrapper
        self.stock_code = stock_code
        self.order_req_df = None

    def query(self):
        self.order_req_df = self.kiwoom_wrapper.get_buy_order_request(self.stock_code)

    # 새로운 체결이 발생 했다면 주문을 취소
    def cancel_if_new_chejan_occur(self):
        total_new_chejan_quantity = 0

        # 주문 기록 중 '매수' 주문만 필터링
        buy_order_req_df = self.order_req_df[self.order_req_df['주문구분'] == '+매수']

        for i, row in buy_order_req_df.iterrows():
            # 100주가 온전히 체결 되었는가?
            if int(row['체결량']) == 100:
                order_no = row['주문번호']
                # 100주 체결되었으므로 기존 주문 취소
                self.kiwoom_wrapper.cancel_buy_order(self.stock_code, order_no)
                total_new_chejan_quantity += int(row['체결량'])
                time.sleep(0.25)
        return total_new_chejan_quantity

    def get_total_chejan_quantity(self):
        total_chejan_quantity = 0
        buy_order_req_df = self.order_req_df[self.order_req_df['주문구분'] == '+매수']
        for i, row in buy_order_req_df.iterrows():
            total_chejan_quantity += int(row['체결량'])

        return total_chejan_quantity

