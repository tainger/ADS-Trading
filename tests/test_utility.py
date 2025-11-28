"""
工具函数测试模块
测试各种工具函数的功能和正确性，包括数值处理、K线生成器和数组管理器等
"""
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
    """测试各种工具函数的功能"""
    
    def test_round_to(self):
        """测试数值四舍五入函数
        验证round_to函数是否能够正确地将数值四舍五入到指定的精度
        """
        # 测试基本的四舍五入
        self.assertEqual(round_to(1.234, 0.01), Decimal('1.23'), "四舍五入到两位小数失败")
        # 测试负数四舍五入
        self.assertEqual(round_to(-1.235, 0.01), Decimal('-1.24'), "负数四舍五入失败")

    def test_floor_to(self):
        """测试数值向下取整函数
        验证floor_to函数是否能够正确地将数值向下取整到指定的精度
        """
        # 测试基本的向下取整
        self.assertEqual(floor_to(1.234, 0.1), Decimal('1.2'), "向下取整到一位小数失败")
        # 测试负数向下取整（注意：floor_to对负数的处理是向零方向取整）
        self.assertEqual(floor_to(-1.234, 0.1), Decimal('-1.2'), "负数向下取整失败")

    def test_ceil_to(self):
        """测试数值向上取整函数
        验证ceil_to函数是否能够正确地将数值向上取整到指定的精度
        """
        # 测试基本的向上取整
        self.assertEqual(ceil_to(1.234, 0.1), Decimal('1.3'), "向上取整到一位小数失败")
        # 测试负数向上取整（注意：ceil_to对负数的处理是向远离零方向取整）
        self.assertEqual(ceil_to(-1.234, 0.1), Decimal('-1.3'), "负数向上取整失败")

    def test_get_digits(self):
        """测试获取小数位数函数
        验证get_digits函数是否能够正确地计算数值的小数位数
        """
        # 测试一位小数
        self.assertEqual(get_digits(0.1), 1, "获取一位小数位数失败")
        # 测试多位小数
        self.assertEqual(get_digits(1.2345), 4, "获取四位小数位数失败")
        # 测试浮点数表示的整数
        self.assertEqual(get_digits(1.0), 1, "获取浮点数整数小数位数失败")
        # 测试科学计数法
        self.assertEqual(get_digits(1e-5), 5, "获取科学计数法小数位数失败")
        # 测试大整数
        self.assertEqual(get_digits(10000), 0, "获取大整数小数位数失败")

    def test_extract_vt_symbol(self):
        """测试解析交易对符号函数
        验证extract_vt_symbol函数是否能够正确地从vt_symbol中解析出symbol和exchange
        """
        symbol, exchange = extract_vt_symbol("BTC.BINANCE")
        self.assertEqual(symbol, "BTC", "解析交易对符号失败")
        self.assertEqual(exchange, Exchange("BINANCE"), "解析交易所信息失败")
        
        # 测试其他交易对
        symbol, exchange = extract_vt_symbol("ETH.BINANCE")
        self.assertEqual(symbol, "ETH", "解析ETH交易对符号失败")
        self.assertEqual(exchange, Exchange("BINANCE"), "解析ETH交易所信息失败")

    def test_generate_vt_symbol(self):
        """测试生成交易对符号函数
        验证generate_vt_symbol函数是否能够正确地生成vt_symbol
        """
        vt_symbol = generate_vt_symbol("BTC", Exchange("BINANCE"))
        self.assertEqual(vt_symbol, "BTC.BINANCE", "生成交易对符号失败")
        
        # 测试其他交易对
        vt_symbol = generate_vt_symbol("ETH", Exchange("BINANCE"))
        self.assertEqual(vt_symbol, "ETH.BINANCE", "生成ETH交易对符号失败")


class TestBarGenerator(unittest.TestCase):
    """测试K线生成器功能"""
    
    def setUp(self):
        """测试环境准备
        创建K线生成器实例，用于测试K线生成功能
        """
        self.bars = []
        self.window_bars = []
        # 创建BarGenerator实例，设置window=5，并监听on_window_bar事件
        self.bg = BarGenerator(on_bar=self.bars.append, window=5, on_window_bar=self.window_bars.append)

    def test_update_tick(self):
        """测试通过行情数据更新K线
        验证BarGenerator是否能够正确地根据行情数据更新K线
        """
        # 创建测试用的行情数据
        tick = TickData(
            symbol="BTC",
            exchange=Exchange("BINANCE"),
            datetime=datetime(2023, 1, 1, 0, 0, 0),
            gateway_name="DB",
            last_price=100,
            high_price=100,
            low_price=100,
            open_interest=0,
            volume=1
        )
        
        # 更新K线生成器
        self.bg.update_tick(tick)
        
        # 验证K线生成器状态
        self.assertIsNotNone(self.bg.bar, "K线对象未创建")
        self.assertEqual(self.bg.bar.open_price, 100, "K线开盘价不正确")
        self.assertEqual(self.bg.bar.high_price, 100, "K线最高价不正确")
        self.assertEqual(self.bg.bar.low_price, 100, "K线最低价不正确")
        self.assertEqual(self.bg.bar.close_price, 100, "K线收盘价不正确")

    def test_update_bar(self):
        """测试通过K线数据更新K线
        验证BarGenerator类的update_bar方法是否能正确处理K线数据
        """
        # 创建5根连续的K线数据
        for i in range(5):
            bar = BarData(
                symbol="BTC",
                exchange=Exchange("BINANCE"),
                datetime=datetime(2023, 1, 1, 0, i, 0),
                interval=Interval("1m"),
                gateway_name="DB",
                open_price=100 + i,
                high_price=101 + i,
                low_price=99 + i,
                close_price=100.5 + i,
                volume=1 + i,
                turnover=100.5 + i,
                open_interest=0
            )
            
            # 调用update_bar方法
            self.bg.update_bar(bar)
        
        # 验证是否生成了一根5分钟的K线
        self.assertEqual(len(self.window_bars), 1, "5分钟K线未被生成")


class TestArrayManager(unittest.TestCase):
    """测试数组管理器功能"""
    
    def setUp(self):
        """测试环境准备
        创建数组管理器实例并添加测试数据
        """
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
        """测试简单移动平均线计算
        验证ArrayManager是否能够正确地计算简单移动平均线
        """
        sma = self.am.sma(2)
        self.assertIsInstance(sma, float, "SMA返回值类型不正确")
        
        # 验证SMA计算结果（(101 + 102) / 2 = 101.5）
        self.assertAlmostEqual(sma, 101.5, "SMA计算结果不正确")

    def test_rsi(self):
        """测试相对强弱指数计算
        验证ArrayManager是否能够正确地计算相对强弱指数
        """
        rsi = self.am.rsi(2)
        self.assertIsInstance(rsi, float, "RSI返回值类型不正确")
        # RSI应该在0-100之间
        self.assertGreaterEqual(rsi, 0, "RSI值小于0")
        self.assertLessEqual(rsi, 100, "RSI值大于100")

    def test_macd(self):
        """测试移动平均收敛发散指标计算
        验证ArrayManager是否能够正确地计算MACD指标
        """
        macd, signal, hist = self.am.macd(12, 26, 9)  # 添加必要的参数
        self.assertIsInstance(macd, float, "MACD返回值类型不正确")
        self.assertIsInstance(signal, float, "MACD信号线返回值类型不正确")
        self.assertIsInstance(hist, float, "MACD柱状图返回值类型不正确")

    def test_boll(self):
        """测试布林带指标计算
        验证ArrayManager是否能够正确地计算布林带指标
        """
        upper, lower = self.am.boll(2, 2)  # boll方法只返回upper和lower两个值
        self.assertIsInstance(upper, float, "布林带上轨返回值类型不正确")
        self.assertIsInstance(lower, float, "布林带下轨返回值类型不正确")
        
        # 验证上下轨关系
        self.assertGreaterEqual(upper, lower, "布林带上轨小于下轨")


if __name__ == "__main__":
    unittest.main()