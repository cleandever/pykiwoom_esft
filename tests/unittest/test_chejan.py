import unittest

from src.kiwoom.chejan import Chejan

# 접수
chejan_raw1 = {'gubun': '0', '9201': '5068904411', '9203': '0008048', '9205': '', '9001': 'A227100', '912': 'JJ', '913': '접수', '302': '퀀텀온                                  ', '900': '1', '901': '0', '902': '1', '903': '0', '904': '0000000', '905': '+매수', '906': '시장가', '907': '2', '908': '090853', '909': '', '910': '', '911': '', '10': '-1510', '27': '-1510', '28': '-1495', '914': '', '915': '', '938': '0', '939': '0', '919': '0', '920': '4989', '921': '6601010 ', '922': '00', '923': '00000000', '949': '3', '10010': '+1556', '969': '0', '819': '0'}

# 체결
chejan_raw2 = {'gubun': '0', '9201': '5068904411', '9203': '0008048', '9205': '', '9001': 'A227100', '912': 'JJ', '913': '체결', '302': '퀀텀온                                  ', '900': '1', '901': '0', '902': '0', '903': '1510', '904': '0000000', '905': '+매수', '906': '시장가', '907': '2', '908': '090853', '909': '545', '910': '1510', '911': '1', '10': '-1510', '27': '-1510', '28': '-1495', '914': '1510', '915': '1', '938': '0', '939': '0', '919': '0', '920': '4989', '921': '6601010 ', '922': '00', '923': '00000000', '949': '3', '10010': '+1556', '969': '0', '819': '0'}


class TestChejan(unittest.TestCase):
    def test_is_chejan(self):
        chejan = Chejan(chejan_raw1)
        self.assertFalse(chejan.is_chejan())

        chejan = Chejan(chejan_raw2)
        self.assertTrue(chejan.is_chejan())

    def test_parse_chejan(self):
        chejan = Chejan(chejan_raw2)
        chejan.parse_chejan()
        print(chejan.to_string())

        self.assertEqual(chejan.stock_code, '227100')
        self.assertEqual(chejan.order_no, '0008048')
        self.assertEqual(chejan.order_quantity, 1)
        self.assertEqual(chejan.unit_chejan_quantity, 1)
        self.assertEqual(chejan.chejan_quantity, 1)
