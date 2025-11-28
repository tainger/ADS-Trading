# ADS Trading 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**A**lpha **D**awn **S**tar Trading Framework.

> 在市场的黑夜中，寻找指引方向的黎明之星。

ADS Trading 是一个现代化、高性能的开源量化交易框架。它旨在为交易员和研究者提供一个从策略研究、回测验证到实盘交易的强大一体化解决方案。

### Star History

[![Star History Chart](https://api.star-history.com/svg?repos=tainger/ADS-Trading&type=Date)](https://star-history.com/#tainger/ADS-Trading&Date)

## ✨ 核心特性

*   **🚀 极致性能**：基于向量化计算与异步IO，提供高速的数据处理与回测体验。
*   **📈 全流程覆盖**：集成数据管理、策略开发、回测分析、实盘交易与风险监控。
*   **🧠 AI友好**：深度整合机器学习库（如Scikit-learn, PyTorch），便于开发AI驱动的交易策略。
*   **🔧 模块化设计**：高度解耦的架构，让您可以轻松替换或扩展任何组件（数据接口、执行引擎等）。
*   **📊 丰富可视化**：内置基于Chart.js的交互式图表，深入分析策略表现与交易行为。
*   **🌐 多市场支持**：无缝对接股票、期货、加密货币等多个市场。
*   **📱 响应式UI**：现代化的Web界面，支持桌面和移动端访问。

## 🏗 项目架构

```
ADS-Trading/
├── ads_trading/          # 主源码目录
│   ├── main.py           # 入口文件
│   └── trader/           # 交易核心模块
│       ├── backtest/     # 回测引擎
│       ├── data/         # 数据模块
│       ├── event/        # 事件系统
│       ├── gateway/      # 交易网关
│       ├── strategy/     # 策略模块
│       ├── utility/      # 工具模块
│       └── setting.py    # 配置文件
├── web-ui/               # Web界面
│   ├── public/           # 静态资源
│   ├── src/              # 源代码
│   ├── package.json      # 依赖配置
│   └── .gitignore        # Git忽略文件
├── docs/                 # 文档目录
│   ├── README.md         # 主文档
│   ├── quickstart.md     # 快速开始指南
│   ├── example_strategies.md # 示例策略
│   └── api_reference.md  # API参考
├── tests/                # 测试目录
├── build.py              # 构建脚本
├── requirements.txt      # Python依赖
└── README.md             # 项目说明
```

## 🚀 快速开始

详细的快速开始指南，请参考 [快速开始](docs/quickstart.md)。

### 安装步骤

1.  **克隆仓库**
    ```bash
    git clone https://github.com/yourusername/ADS-Trading.git
    cd ADS-Trading
    ```

2.  **安装Python依赖**
    ```bash
    # 创建虚拟环境（可选但推荐）
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或在Windows上: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
    ```

3.  **安装Web UI依赖**
    ```bash
    cd web-ui
    npm install
    cd ..
    ```

### 运行系统

1.  **运行策略引擎**
    ```bash
    python -m ads_trading.main
    ```

2.  **运行Web UI**
    ```bash
    cd web-ui
    npm start
    ```

3.  **访问Web界面**
    打开浏览器，访问 `http://localhost:3000`

## 📖 文档

*   [**快速开始**](docs/quickstart.md) - 快速安装和配置ADS Trading
*   [**主文档**](docs/README.md) - 系统架构和功能说明
*   [**示例策略**](docs/example_strategies.md) - 各种交易策略示例
*   [**API参考**](docs/api_reference.md) - 核心API的详细说明

## 📊 示例策略

我们提供了多种交易策略示例，帮助您快速上手策略开发。详细请参考 [示例策略](docs/example_strategies.md)。

主要示例包括：

*   **双均线策略** - 基于移动平均线交叉的趋势跟踪策略
*   **RSI策略** - 基于相对强弱指标的超买超卖策略
*   **布林带策略** - 基于价格通道突破的策略
*   **海龟交易策略** - 经典的趋势跟踪策略

## 🛠️ 开发指南

### 策略开发

ADS Trading提供了简洁而强大的策略开发API。您可以通过继承`BaseStrategy`类来开发自己的策略：

```python
from trader.strategy import BaseStrategy
from trader.object import BarData, OrderData, TradeData

class MyStrategy(BaseStrategy):
    def __init__(self, engine, setting=None):
        super().__init__(engine, setting)
        self.pos = 0
    
    def on_bar(self, bar: BarData):
        # 策略逻辑
        if bar.close_price > 10000 and self.pos == 0:
            self.buy(bar.symbol, bar.close_price, 0.1)
        elif bar.close_price < 9000 and self.pos > 0:
            self.sell(bar.symbol, bar.close_price, self.pos)
    
    def on_trade(self, trade: TradeData):
        # 处理成交事件
        if trade.direction == "buy":
            self.pos += trade.quantity
        else:
            self.pos -= trade.quantity
```

更多策略开发的详细信息，请参考 [示例策略](docs/example_strategies.md)。

### 回测

您可以使用回测引擎测试策略的历史表现：

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
print(f"总收益率: {results['total_return']:.2%}")
print(f"年化收益率: {results['annual_return']:.2%}")
print(f"最大回撤: {results['max_drawdown']:.2%}")
```

## 🎨 Web界面

ADS Trading提供了现代化的Web界面，支持：

*   实时市场数据监控
*   价格历史图表分析
*   订单管理
*   持仓查看
*   交易历史记录
*   策略表现分析

Web界面支持响应式设计，可在桌面和移动设备上使用。

## 🔌 市场支持

ADS Trading目前支持以下市场：

*   加密货币市场（Binance, OKX, Coinbase等）
*   股票市场
*   期货市场

## 🤝 贡献

我们欢迎社区贡献！如果您想为ADS Trading贡献代码或文档，请：

1. Fork仓库
2. 创建您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

如果您有任何问题或建议，欢迎通过以下方式联系我们：

*   提交Issue：在GitHub仓库提交Issue
*   发送邮件：your-email@example.com
*   加入社区：我们的社区链接

## 🙏 致谢

感谢所有为ADS Trading做出贡献的开发者和用户！

---

**ADS Trading** - 在市场的黑夜中，寻找指引方向的黎明之星。