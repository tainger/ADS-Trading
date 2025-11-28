# ADS Trading 示例策略

本文档提供了几个常用的量化交易策略示例，帮助您快速了解ADS Trading系统的策略开发方法。

## 1. 双均线策略 (Moving Average Strategy)

双均线策略是最基础的趋势跟踪策略，通过比较短期和长期均线的交叉来产生交易信号。

### 策略原理
- 当短期均线上穿长期均线时（金叉），产生买入信号
- 当短期均线下穿长期均线时（死叉），产生卖出信号

### 策略实现

```python
# trader/strategy/moving_average.py
from trader.strategy import BaseStrategy
from trader.object import BarData, OrderData, TradeData
from trader.constant import Interval
from trader.utility import ArrayManager

class MovingAverageStrategy(BaseStrategy):
    """双均线策略"""
    
    author = "ADS Trading"
    symbol = "BTC/USDT"
    interval = Interval.HOUR
    
    # 策略参数
    fast_window = 10  # 短期均线周期
    slow_window = 30  # 长期均线周期
    
    def __init__(self, engine, setting=None):
        super().__init__(engine, setting)
        self.am = ArrayManager(size=self.slow_window + 1)
        self.fast_ma = None
        self.slow_ma = None
        self.pos = 0  # 当前持仓数量
    
    def on_init(self):
        """策略初始化"""
        self.write_log("策略初始化")
        # 请求历史数据
        self.request_bar_history(self.symbol, self.interval, self.slow_window)
    
    def on_bar(self, bar: BarData):
        """处理K线数据"""
        self.am.update_bar(bar)
        
        if not self.am.inited:
            return
        
        # 计算均线
        self.fast_ma = self.am.sma(self.fast_window)
        self.slow_ma = self.am.sma(self.slow_window)
        
        # 记录日志
        self.write_log(f"{bar.datetime} - 价格: {bar.close_price}, 快线: {self.fast_ma:.2f}, 慢线: {self.slow_ma:.2f}")
        
        # 金叉买入
        if self.fast_ma > self.slow_ma and self.pos == 0:
            self.write_log("金叉信号 - 买入")
            self.buy(self.symbol, bar.close_price, 0.1)
        
        # 死叉卖出
        elif self.fast_ma < self.slow_ma and self.pos > 0:
            self.write_log("死叉信号 - 卖出")
            self.sell(self.symbol, bar.close_price, self.pos)
    
    def on_trade(self, trade: TradeData):
        """处理成交事件"""
        if trade.symbol == self.symbol:
            if trade.direction == "buy":
                self.pos += trade.quantity
            else:
                self.pos -= trade.quantity
            
            self.write_log(f"成交 - {trade.direction} {trade.quantity} {trade.symbol} @ {trade.price}")
    
    def on_order(self, order: OrderData):
        """处理订单事件"""
        self.write_log(f"订单更新 - {order.symbol} {order.status}: {order.volume} @ {order.price}")
```

### 策略配置

在`setting.py`中配置策略：

```python
STRATEGIES = [
    {
        "name": "MovingAverageStrategy",
        "module": "trader.strategy.moving_average",
        "symbol": "BTC/USDT",
        "interval": "1h",
        "parameters": {
            "fast_window": 10,
            "slow_window": 30
        }
    }
]
```

## 2. RSI 策略 (Relative Strength Index)

RSI策略是基于相对强弱指标的超买超卖策略。

### 策略原理
- RSI > 70 时，市场超买，产生卖出信号
- RSI < 30 时，市场超卖，产生买入信号

### 策略实现

```python
# trader/strategy/rsi_strategy.py
from trader.strategy import BaseStrategy
from trader.object import BarData, OrderData, TradeData
from trader.constant import Interval
from trader.utility import ArrayManager

class RSIStrategy(BaseStrategy):
    """RSI超买超卖策略"""
    
    author = "ADS Trading"
    symbol = "ETH/USDT"
    interval = Interval.MINUTE
    
    # 策略参数
    rsi_window = 14  # RSI周期
    overbought = 70  # 超买阈值
    oversold = 30    # 超卖阈值
    
    def __init__(self, engine, setting=None):
        super().__init__(engine, setting)
        self.am = ArrayManager(size=self.rsi_window + 1)
        self.rsi = None
        self.pos = 0
    
    def on_init(self):
        """策略初始化"""
        self.write_log("RSI策略初始化")
        self.request_bar_history(self.symbol, self.interval, self.rsi_window)
    
    def on_bar(self, bar: BarData):
        """处理K线数据"""
        self.am.update_bar(bar)
        
        if not self.am.inited:
            return
        
        # 计算RSI
        self.rsi = self.am.rsi(self.rsi_window)
        
        self.write_log(f"{bar.datetime} - 价格: {bar.close_price}, RSI: {self.rsi:.2f}")
        
        # 超买卖出
        if self.rsi > self.overbought and self.pos > 0:
            self.write_log("RSI超买 - 卖出")
            self.sell(self.symbol, bar.close_price, self.pos)
        
        # 超卖买入
        elif self.rsi < self.oversold and self.pos == 0:
            self.write_log("RSI超卖 - 买入")
            self.buy(self.symbol, bar.close_price, 0.1)
    
    def on_trade(self, trade: TradeData):
        """处理成交事件"""
        if trade.symbol == self.symbol:
            if trade.direction == "buy":
                self.pos += trade.quantity
            else:
                self.pos -= trade.quantity
            
            self.write_log(f"成交 - {trade.direction} {trade.quantity} {trade.symbol} @ {trade.price}")
```

## 3. 布林带策略 (Bollinger Bands)

布林带策略利用价格通道突破来产生交易信号。

### 策略原理
- 价格跌破下轨时，产生买入信号
- 价格突破上轨时，产生卖出信号

### 策略实现

```python
# trader/strategy/bollinger_bands.py
from trader.strategy import BaseStrategy
from trader.object import BarData, OrderData, TradeData
from trader.constant import Interval
from trader.utility import ArrayManager

class BollingerBandsStrategy(BaseStrategy):
    """布林带策略"""
    
    author = "ADS Trading"
    symbol = "BTC/USDT"
    interval = Interval.HOUR
    
    # 策略参数
    bb_window = 20   # 布林带周期
    bb_dev = 2.0     # 标准差倍数
    
    def __init__(self, engine, setting=None):
        super().__init__(engine, setting)
        self.am = ArrayManager(size=self.bb_window + 1)
        self.bb_mid = None  # 中轨
        self.bb_upper = None  # 上轨
        self.bb_lower = None  # 下轨
        self.pos = 0
    
    def on_init(self):
        """策略初始化"""
        self.write_log("布林带策略初始化")
        self.request_bar_history(self.symbol, self.interval, self.bb_window)
    
    def on_bar(self, bar: BarData):
        """处理K线数据"""
        self.am.update_bar(bar)
        
        if not self.am.inited:
            return
        
        # 计算布林带
        self.bb_mid = self.am.sma(self.bb_window)
        std_dev = self.am.std(self.bb_window)
        self.bb_upper = self.bb_mid + self.bb_dev * std_dev
        self.bb_lower = self.bb_mid - self.bb_dev * std_dev
        
        self.write_log(f"{bar.datetime} - 价格: {bar.close_price}, BB: [{self.bb_lower:.2f}, {self.bb_mid:.2f}, {self.bb_upper:.2f}]")
        
        # 突破上轨卖出
        if bar.close_price > self.bb_upper and self.pos > 0:
            self.write_log("突破上轨 - 卖出")
            self.sell(self.symbol, bar.close_price, self.pos)
        
        # 跌破下轨买入
        elif bar.close_price < self.bb_lower and self.pos == 0:
            self.write_log("跌破下轨 - 买入")
            self.buy(self.symbol, bar.close_price, 0.1)
    
    def on_trade(self, trade: TradeData):
        """处理成交事件"""
        if trade.symbol == self.symbol:
            if trade.direction == "buy":
                self.pos += trade.quantity
            else:
                self.pos -= trade.quantity
            
            self.write_log(f"成交 - {trade.direction} {trade.quantity} {trade.symbol} @ {trade.price}")
```

## 4. 海龟交易策略 (Turtle Trading)

海龟交易策略是经典的趋势跟踪策略，基于突破和资金管理规则。

### 策略原理
- 突破20日最高价买入
- 突破10日最低价卖出
- 固定风险的资金管理

### 策略实现

```python
# trader/strategy/turtle_strategy.py
from trader.strategy import BaseStrategy
from trader.object import BarData, OrderData, TradeData
from trader.constant import Interval
from trader.utility import ArrayManager

class TurtleStrategy(BaseStrategy):
    """海龟交易策略"""
    
    author = "ADS Trading"
    symbol = "BTC/USDT"
    interval = Interval.DAY
    
    # 策略参数
    entry_length = 20  # 入场突破周期
    exit_length = 10   # 出场突破周期
    risk_percent = 0.01  # 每笔交易风险占比
    
    def __init__(self, engine, setting=None):
        super().__init__(engine, setting)
        self.am = ArrayManager(size=self.entry_length + 1)
        self.pos = 0
        self.entry_price = 0
        self.atr = 0  # 平均真实波动幅度
    
    def on_init(self):
        """策略初始化"""
        self.write_log("海龟策略初始化")
        self.request_bar_history(self.symbol, self.interval, self.entry_length)
    
    def on_bar(self, bar: BarData):
        """处理K线数据"""
        self.am.update_bar(bar)
        
        if not self.am.inited:
            return
        
        # 计算ATR
        self.atr = self.am.atr(14)
        
        # 计算突破价格
        highest = self.am.high_array[-self.entry_length:].max()
        lowest = self.am.low_array[-self.exit_length:].min()
        
        # 计算头寸大小
        account_balance = self.get_balance()
        risk_per_trade = account_balance * self.risk_percent
        position_size = risk_per_trade / (self.atr * 2) if self.atr > 0 else 0
        position_size = round(position_size, 2)  # 保留两位小数
        
        self.write_log(f"{bar.datetime} - 价格: {bar.close_price}, ATR: {self.atr:.2f}, 头寸大小: {position_size}")
        
        # 突破买入
        if bar.close_price > highest and self.pos <= 0:
            self.write_log("突破买入信号")
            self.buy(self.symbol, bar.close_price, position_size)
        
        # 突破卖出
        elif bar.close_price < lowest and self.pos >= 0:
            self.write_log("突破卖出信号")
            if self.pos > 0:
                self.sell(self.symbol, bar.close_price, self.pos)
    
    def on_trade(self, trade: TradeData):
        """处理成交事件"""
        if trade.symbol == self.symbol:
            if trade.direction == "buy":
                self.pos += trade.quantity
                self.entry_price = trade.price
            else:
                self.pos -= trade.quantity
            
            self.write_log(f"成交 - {trade.direction} {trade.quantity} {trade.symbol} @ {trade.price}")
    
    def get_balance(self):
        """获取账户余额"""
        # 在实盘环境中，应从引擎获取真实账户余额
        # 回测环境中，使用初始资金
        return self.engine.initial_capital if hasattr(self.engine, 'initial_capital') else 10000
```

## 5. 多策略组合 (Strategy Combination)

ADS Trading支持同时运行多个策略，可以创建策略组合来分散风险。

### 策略配置示例

```python
STRATEGIES = [
    # 双均线策略
    {
        "name": "MovingAverageStrategy",
        "module": "trader.strategy.moving_average",
        "symbol": "BTC/USDT",
        "interval": "1h",
        "parameters": {
            "fast_window": 10,
            "slow_window": 30
        }
    },
    # RSI策略
    {
        "name": "RSIStrategy",
        "module": "trader.strategy.rsi_strategy",
        "symbol": "ETH/USDT",
        "interval": "30m",
        "parameters": {
            "rsi_window": 14,
            "overbought": 70,
            "oversold": 30
        }
    },
    # 布林带策略
    {
        "name": "BollingerBandsStrategy",
        "module": "trader.strategy.bollinger_bands",
        "symbol": "ADA/USDT",
        "interval": "1h",
        "parameters": {
            "bb_window": 20,
            "bb_dev": 2.0
        }
    }
]
```

## 策略开发最佳实践

1. **参数优化**：使用回测系统测试不同参数组合，找到最优参数
2. **风险管理**：始终设置止损，控制每笔交易的风险
3. **日志记录**：详细记录策略运行过程，便于调试和分析
4. **性能监控**：定期分析策略表现，及时调整
5. **回测验证**：在实盘运行前，充分进行回测验证

## 策略测试和回测

使用回测引擎测试策略：

```python
from trader.backtest import BacktestEngine
from trader.strategy.moving_average import MovingAverageStrategy
from trader.constant import Interval
from datetime import datetime

# 初始化回测引擎
engine = BacktestEngine()

# 设置回测参数
engine.set_parameters(
    strategy=MovingAverageStrategy,
    symbol="BTC/USDT",
    interval=Interval.HOUR,
    start=datetime(2023, 1, 1),
    end=datetime(2023, 12, 31),
    initial_capital=10000,
    slippage=0.001,
    commission=0.0002
)

# 运行回测
engine.run()

# 获取回测结果
results = engine.get_results()
print("回测结果:")
print(f"总收益率: {results['total_return']:.2%}")
print(f"年化收益率: {results['annual_return']:.2%}")
print(f"最大回撤: {results['max_drawdown']:.2%}")
print(f"夏普比率: {results['sharpe_ratio']:.2f}")
print(f"总交易次数: {results['total_trades']}")
```

---

以上示例策略涵盖了不同类型的交易策略，您可以根据自己的需求进行修改和扩展。在实盘运行前，务必进行充分的回测和风险评估。

有关更多策略开发的详细信息，请参考「策略开发指南」部分。
