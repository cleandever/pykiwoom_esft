chejan_fid = {
    '주문상태': '913',
    '종목코드': '9001',
    '주문번호': '9203',
    '주문수량': '900',
    '단위체결량': '915',
    '체결량': '911',
}


class Chejan:
    def __init__(self, chejan_raw):
        self.chejan_raw = chejan_raw
        self.stock_code = chejan_raw[chejan_fid['종목코드']][1:]

        self.order_no = ''
        self.order_quantity = 0
        self.unit_chejan_quantity = 0
        self.chejan_quantity = 0

    def is_chejan(self):
        order_status_fid = chejan_fid['주문상태']
        if order_status_fid in self.chejan_raw and self.chejan_raw[order_status_fid] == '체결':
            return True
        return False

    def parse_chejan(self):
        self.order_no = self.chejan_raw[chejan_fid['주문번호']]
        self.order_quantity = int(self.chejan_raw[chejan_fid['주문수량']])
        self.unit_chejan_quantity = int(self.chejan_raw[chejan_fid['단위체결량']])
        self.chejan_quantity = int(self.chejan_raw[chejan_fid['체결량']])

    def to_string(self):
        return f'체결 - ' \
               f'종목코드 : {self.stock_code}, ' \
               f'주문번호 : {self.order_no}, ' \
               f'주문수량 : {self.order_quantity}, ' \
               f'단위체결량 : {self.unit_chejan_quantity}, ' \
               f'체결수량 : {self.chejan_quantity}'
