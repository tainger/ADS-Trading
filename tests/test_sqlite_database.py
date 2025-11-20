# tests/test_sqlite_database.py

import unittest
import os
from datetime import datetime
from ads_trading.trader.dbconnectors.sqlite_database import SqliteDatabase, DbBarData, DbTickData, DbBarOverview
from ads_trading.trader.constant import Exchange, Interval
from ads_trading.trader.object import BarData

class TestSqliteDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_db_path = "test_database.db"
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)
        import ads_trading.trader.utility
        ads_trading.trader.utility.get_file_path = lambda x: cls.test_db_path

    def setUp(self):
        self.db = SqliteDatabase()

    def tearDown(self):
        self.db.db.drop_tables([DbBarData, DbTickData, DbBarOverview])
        self.db.db.close()
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_save_and_load_bar_data(self):
        bar = BarData(
            symbol="BTC",
            exchange=Exchange("BINANCE"),
            datetime=datetime(2023, 1, 1, 0, 0, 0),
            interval=Interval("1m"),
            volume=1.0,
            open_interest=0.0,
            open_price=100.0,
            high_price=101.0,
            low_price=99.0,
            close_price=100.5,
            gateway_name="DB"
        )
        result = self.db.save_bar_data([bar])
        self.assertTrue(result)
        bars = self.db.load_bar_data(
            symbol="BTC",
            exchange=Exchange("BINANCE"),
            interval=Interval("1m"),
            start=datetime(2023, 1, 1, 0, 0, 0),
            end=datetime(2023, 1, 1, 0, 1, 0)
        )
        self.assertEqual(len(bars), 1)
        self.assertEqual(bars[0].symbol, "BTC")

if __name__ == "__main__":
    unittest.main()