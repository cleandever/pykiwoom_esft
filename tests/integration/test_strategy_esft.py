import unittest
from unittest.mock import patch

from src.config_esft import ConfigEsft
from src.kiwoom.kiwoom_wrapper import KiwoomWrapper
from src.strategy_esft import main
from src.util.helper import Helper


class TestStrategyEsft(unittest.TestCase):
    def test_main(self):
        with (patch.object(Helper, 'is_now_time_under', return_value=False),
              patch.object(KiwoomWrapper, 'login', side_effect=None)
              ):
                main()
