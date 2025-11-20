import unittest
from decimal import Decimal
from ads_trading.trader.utility import (
    round_to, floor_to, ceil_to, get_digits,
    BarGenerator, ArrayManager, extract_vt_symbol, generate_vt_symbol
)
from ads_trading.trader.constant import Exchange, Interval
from ads_trading.trader.object import BarData, TickData
from datetime import datetime

class TestUtilityFunctions(unittest.TestCase):
    def test_round_to(self):
        self.assertEqual(round_to(1.234, 0.01), Decimal('1.23'))
        self.assertEqual(round_to(1.235, 0.01), Decimal('1.24'))

    def test_floor_to(self):
        self.assertEqual(floor_to(1.239, 0.01), Decimal('1.23'))

    def test_ceil_to(self):
        self.assertEqual(ceil_to(1.231, 0.01), Decimal('1.24'))

    def test_get_digits(self):
        self.assertEqual(get_digits(1.2345), 4)
        self.assertEqual(get_digits(1.0), 1)
        self.assertEqual(get_digits(1e-5), 5)

    def test_extract_vt_symbol(self):
        symbol, exchange = extract_vt_symbol("BTC.BINANCE")
        self.assertEqual(symbol, "BTC")
        self.assertEqual(exchange, Exchange("BINANCE"))

    def test_generate_vt_symbol(self):
        vt_symbol = generate_vt_symbol("BTC", Exchange("BINANCE"))
        self.assertEqual(vt_symbol, "BTC.BINANCE")

class TestBarGenerator(unittest.TestCase):
    def setUp(self):
        self.bars = []
        self.bg = BarGenerator(on_bar=self.bars.append)

    def test_update_tick(self):
        tick = TickData(
            symbol="BTC",
            exchange=Exchange("BINANCE"),
            datetime=datetime(2023, 1, 1, 0, 0, 0),
            gateway_name="DB",
            last_price=100,
            high_price=100,
            low_price=100,
            open_interest=0,
            volume=1,
            turnover=100
        )
        self.bg.update_tick(tick)
        self.assertIsNotNone(self.bg.bar)
        self.assertEqual(self.bg.bar.open_price, 100)

class TestArrayManager(unittest.TestCase):
    def setUp(self):
        self.am = ArrayManager(size=3)
        for i in range(3):
            bar = BarData(
                symbol="BTC",
                exchange=Exchange("BINANCE"),
                datetime=datetime(2023, 1, 1, 0, 0, i),
                gateway_name="DB",
                open_price=100 + i,
                high_price=101 + i,
                low_price=99 + i,
                close_price=100 + i,
                volume=10 + i,
                turnover=1000 + i,
                open_interest=0
            )
            self.am.update_bar(bar)

    def test_sma(self):
        sma = self.am.sma(2)
        self.assertIsInstance(sma, float)

    def test_rsi(self):
        rsi = self.am.rsi(2)
        self.assertIsInstance(rsi, float)

if __name__ == "__main__":
    unittest.main()