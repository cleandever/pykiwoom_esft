import unittest

from src.config_esft import ConfigEsft
from src.kiwoom.kiwoom_wrapper import KiwoomWrapper


class KiwoomTest(unittest.TestCase):
    kiwoom_wrapper = None

    @classmethod
    def setUpClass(cls):
        if cls.kiwoom_wrapper is None:
            cls.kiwoom_wrapper = KiwoomWrapper(ConfigEsft.acc_no)
            cls.kiwoom_wrapper.login()

