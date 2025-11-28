# ADS Trading 快速开始指南

本指南将帮助您快速安装、配置和运行ADS Trading量化交易系统。

## 1. 系统要求

- Python 3.8 或更高版本
- Node.js 14 或更高版本
- npm 6 或更高版本
- SQLite3（用于数据存储）

## 2. 安装步骤

### 2.1 克隆仓库

```bash
git clone https://github.com/yourusername/ADS-Trading.git
cd ADS-Trading
```

### 2.2 安装Python依赖

```bash
# 创建虚拟环境（可选但推荐）
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或在Windows上: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2.3 安装Web UI依赖

```bash
cd web-ui
npm install
cd ..
```

## 3. 配置系统

### 3.1 主配置文件

系统主配置文件位于 `ads_trading/trader/setting.py`。您可以根据需要修改以下配置：

```python
# 基本配置
ENGINE_NAME = "ADS Trading Engine"
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# 数据源配置
DATA_SOURCE = "binance"  # binance, okx, mock 等
DATA_FEED_URL = "wss://stream.binance.com:9443/ws"
API_KEY = "your_api_key"
API_SECRET = "your_api_secret"

# 策略配置
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

# 回测配置
BACKTEST = {
    "initial_capital": 10000,
    "slippage": 0.001,
    "commission": 0.0002
}

# Web UI配置
WEB_UI_PORT = 3000
API_SERVER_PORT = 5000
```

### 3.2 环境变量配置（可选）

您也可以通过环境变量配置敏感信息，避免将API密钥等信息硬编码到配置文件中：

```bash
export ADS_API_KEY="your_api_key"
export ADS_API_SECRET="your_api_secret"
```

## 4. 运行系统

### 4.1 运行策略引擎

```bash
python -m ads_trading.main
```

### 4.2 运行Web UI

在另一个终端窗口中运行：

```bash
cd web-ui
npm start
```

Web UI将在 `http://localhost:3000` 启动，API服务器将在 `http://localhost:5000` 运行。

## 5. 首次使用

### 5.1 访问Web UI

打开浏览器，访问 `http://localhost:3000`，您将看到ADS Trading的主界面：

![ADS Trading 主界面](../assets/web_ui_main.png)

### 5.2 查看市场数据

在「市场」标签页中，您可以查看实时市场数据和价格走势图：

![市场数据](../assets/market_data.png)

### 5.3 提交订单

在「交易」标签页中，您可以手动提交交易订单：

![交易表单](../assets/trading_form.png)

### 5.4 查看持仓

在「持仓」标签页中，您可以查看当前持仓情况：

![持仓信息](../assets/positions.png)

### 5.5 查看历史记录

在「历史」标签页中，您可以查看历史交易记录：

![历史记录](../assets/history.png)

### 5.6 查看策略表现

在「表现」标签页中，您可以查看策略的绩效指标和图表：

![策略表现](../assets/performance.png)

## 6. 运行回测

### 6.1 创建回测脚本

创建一个回测脚本 `backtest_example.py`：

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

# 打印回测结果
print("回测结果摘要:")
print(f"初始资金: {results['initial_capital']}")
print(f"最终资金: {results['final_capital']:.2f}")
print(f"总收益率: {results['total_return']:.2%}")
print(f"年化收益率: {results['annual_return']:.2%}")
print(f"最大回撤: {results['max_drawdown']:.2%}")
print(f"夏普比率: {results['sharpe_ratio']:.2f}")
print(f"总交易次数: {results['total_trades']}")
print(f"胜率: {results['win_rate']:.2%}")
```

### 6.2 运行回测

```bash
python backtest_example.py
```

### 6.3 分析回测结果

回测完成后，您将看到类似以下的输出：

```
回测结果摘要:
初始资金: 10000
最终资金: 12345.67
总收益率: 23.46%
年化收益率: 23.46%
最大回撤: 15.23%
夏普比率: 1.45
总交易次数: 45
胜率: 55.56%
```

## 7. 开发自定义策略

### 7.1 创建策略文件

在 `ads_trading/trader/strategy/` 目录下创建一个新的策略文件，例如 `my_strategy.py`：

```python
from trader.strategy import BaseStrategy
from trader.object import BarData, OrderData, TradeData
from trader.constant import Interval
from trader.utility import ArrayManager

class MyStrategy(BaseStrategy):
    """我的自定义策略"""
    
    author = "Your Name"
    symbol = "BTC/USDT"
    interval = Interval.HOUR
    
    # 策略参数
    parameter1 = 10
    parameter2 = 30
    
    def __init__(self, engine, setting=None):
        super().__init__(engine, setting)
        self.am = ArrayManager(size=self.parameter2 + 1)
        self.pos = 0
    
    def on_init(self):
        """策略初始化"""
        self.write_log("策略初始化")
        self.request_bar_history(self.symbol, self.interval, self.parameter2)
    
    def on_bar(self, bar: BarData):
        """处理K线数据"""
        self.am.update_bar(bar)
        
        if not self.am.inited:
            return
        
        # 实现您的策略逻辑
        # 例如：
        if bar.close_price > self.am.sma(self.parameter1) and self.pos == 0:
            self.buy(self.symbol, bar.close_price, 0.1)
        elif bar.close_price < self.am.sma(self.parameter1) and self.pos > 0:
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

### 7.2 配置策略

在 `setting.py` 中添加您的策略：

```python
STRATEGIES = [
    # ... 其他策略
    {
        "name": "MyStrategy",
        "module": "trader.strategy.my_strategy",
        "symbol": "BTC/USDT",
        "interval": "1h",
        "parameters": {
            "parameter1": 10,
            "parameter2": 30
        }
    }
]
```

### 7.3 运行策略

重新启动策略引擎：

```bash
python -m ads_trading.main
```

## 8. 常见问题

### 8.1 无法连接到交易所API

- 检查API密钥和密钥是否正确
- 确保网络连接正常
- 检查防火墙设置，确保端口80、443、9443等已开放

### 8.2 Web UI无法加载数据

- 确保API服务器正在运行（端口5000）
- 检查浏览器控制台是否有错误信息
- 确认CORS设置正确

### 8.3 回测结果不准确

- 检查数据质量，确保历史数据完整
- 调整回测参数，如滑点、手续费等
- 确保策略逻辑正确

## 9. 获取帮助

如果您遇到问题，可以通过以下方式获取帮助：

- 查看完整文档：`docs/README.md`
- 查看示例策略：`docs/example_strategies.md`
- 查看API参考：`docs/api_reference.md`
- 提交Issue：在GitHub仓库提交Issue

## 10. 下一步

- 学习更多策略示例：查看 `docs/example_strategies.md`
- 深入了解策略开发：查看 `docs/strategy_development.md`
- 了解系统架构：查看 `docs/architecture.md`
- 配置实盘交易：查看 `docs/live_trading.md`

---

恭喜！您已经成功安装并运行了ADS Trading系统。现在您可以开始使用它进行量化交易了。
