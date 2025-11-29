# tests/test_sqlite_database.py
"""
SQLite数据库测试模块
测试数据库连接、K线数据的保存和加载功能
"""

import unittest
import os
from datetime import datetime
from ads_trading.trader.dbconnectors.sqlite_database import SqliteDatabase
from ads_trading.trader.constant import Exchange, Interval
from ads_trading.trader.object import BarData, TickData


class TestSqliteDatabase(unittest.TestCase):
    """SQLite数据库测试类"""

    def setUp(self):
        """测试环境准备
        在每个测试方法执行前创建数据库连接实例
        """
        self.db = SqliteDatabase()

    def tearDown(self):
        """测试环境清理
        在每个测试方法执行后关闭数据库连接
        """
        # 清理测试创建的临时文件（如果有）
        if hasattr(self.db, 'db_path') and os.path.exists(self.db.db_path):
            os.remove(self.db.db_path)

    def test_save_and_load_bar_data(self):
        """测试K线数据的保存和加载功能
        1. 创建K线数据对象
        2. 保存K线数据到数据库
        3. 从数据库加载K线数据
        4. 验证加载的数据与保存的数据一致
        """
        # 创建测试用的K线数据
        bar = BarData(
            symbol="BTC",
            exchange=Exchange("BINANCE"),
            datetime=datetime(2023, 1, 2, 0, 0, 0),
            interval=Interval("1m"),
            volume=1.0,
            open_interest=0.0,
            open_price=100.0,
            high_price=101.0,
            low_price=99.0,
            close_price=100.5,
            gateway_name="DB"
        )
        
        # 测试保存K线数据
        save_result = self.db.save_bar_data([bar])
        self.assertTrue(save_result, "K线数据保存失败")
        
        # 测试加载K线数据
        loaded_bars = self.db.load_bar_data(
            symbol="BTC",
            exchange=Exchange("BINANCE"),
            interval=Interval("1m"),
            start=datetime(2023, 1, 1, 0, 0, 0),
            end=datetime(2023, 1, 1, 0, 1, 0)
        )
        
        # 验证加载的数据数量正确
        self.assertEqual(len(loaded_bars), 1, "加载的K线数据数量不正确")
        
        # 验证加载的数据内容正确
        self.assertEqual(loaded_bars[0].symbol, "BTC", "K线数据的交易对符号不正确")
        self.assertEqual(loaded_bars[0].exchange, Exchange("BINANCE"), "K线数据的交易所信息不正确")
        self.assertEqual(loaded_bars[0].close_price, 100.5, "K线数据的收盘价不正确")

    def test_save_and_load_tick_data(self):
        """测试行情数据的保存和加载功能
        1. 创建行情数据对象
        2. 保存行情数据到数据库
        3. 从数据库加载行情数据
        4. 验证加载的数据与保存的数据一致
        """
        # 创建测试用的行情数据
        tick = TickData(
            symbol="BTC",
            exchange=Exchange("BINANCE"),
            datetime=datetime(2023, 1, 1, 0, 0, 0, 123456),
            gateway_name="DB",
            last_price=100.5,
            high_price=101.0,
            low_price=99.0,
            volume=1.0,
            turnover=100.5,
            open_interest=0.0,
            open_price=100.0,
            bid_price_1=100.4,
            bid_volume_1=0.5,
            ask_price_1=100.6,
            ask_volume_1=0.5
        )
        
        # 测试保存行情数据
        save_result = self.db.save_tick_data([tick])
        self.assertTrue(save_result, "行情数据保存失败")
        
        # 测试加载行情数据
        loaded_ticks = self.db.load_tick_data(
            symbol="BTC",
            exchange=Exchange("BINANCE"),
            start=datetime(2023, 1, 1, 0, 0, 0),
            end=datetime(2023, 1, 1, 0, 0, 1)
        )
        
        # 验证加载的数据数量正确
        self.assertEqual(len(loaded_ticks), 1, "加载的行情数据数量不正确")
        
        # 验证加载的数据内容正确
        self.assertEqual(loaded_ticks[0].symbol, "BTC", "行情数据的交易对符号不正确")
        self.assertEqual(loaded_ticks[0].last_price, 100.5, "行情数据的最新价格不正确")
        self.assertEqual(loaded_ticks[0].bid_price_1, 100.4, "行情数据的买一价不正确")
        self.assertEqual(loaded_ticks[0].ask_price_1, 100.6, "行情数据的卖一价不正确")


if __name__ == "__main__":
    unittest.main()
