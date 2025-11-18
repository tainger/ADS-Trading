# ADS Trading 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**A**lpha **D**awn **S**tar Trading Framework.

> 在市场的黑夜中，寻找指引方向的黎明之星。

ADS Trading 是一个现代化、高性能的开源量化交易框架。它旨在为交易员和研究者提供一个从策略研究、回测验证到实盘交易的强大一体化解决方案。

## ✨ 核心特性

*   **🚀 极致性能**：基于向量化计算与异步IO，提供高速的数据处理与回测体验。
*   **📈 全流程覆盖**：集成数据管理、策略开发、回测分析、实盘交易与风险监控。
*   **🧠 AI友好**：深度整合机器学习库（如Scikit-learn, PyTorch），便于开发AI驱动的交易策略。
*   **🔧 模块化设计**：高度解耦的架构，让您可以轻松替换或扩展任何组件（数据接口、执行引擎等）。
*   **📊 丰富可视化**：内置基于Plotly的交互式图表，深入分析策略表现与交易行为。
*   **🌐 多市场支持**：无缝对接股票、期货、加密货币等多个市场。

## 🏗 项目架构
```java
ADS-Trading/
├── ads_core/ # 核心引擎
│ ├── data_handler # 统一数据接口
│ ├── strategy # 策略基类与引擎
│ ├── backtest # 向量化/事件驱动回测引擎
│ └── live # 实盘交易引擎
├── ads_models/ # 机器学习模型库
├── ads_data/ # 数据获取与管理工具
├── ads_analytics/ # 绩效分析与可视化
├── ads_brokers/ # 各券商/交易所接口适配
├── examples/ # 示例策略与教程
└── tests/ # 测试套件ADS-Trading/
├── ads_core/ # 核心引擎
│ ├── data_handler # 统一数据接口
│ ├── strategy # 策略基类与引擎
│ ├── backtest # 向量化/事件驱动回测引擎
│ └── live # 实盘交易引擎
├── ads_models/ # 机器学习模型库
├── ads_data/ # 数据获取与管理工具
├── ads_analytics/ # 绩效分析与可视化
├── ads_brokers/ # 各券商/交易所接口适配
├── examples/ # 示例策略与教程
└── tests/ # 测试套件
```

## 🚀 快速开始

###  prerequisites

*   Python 3.8 或更高版本
*   pip 包管理器

### 安装

1.  **克隆仓库**
    ```bash
    git clone https://github.com/your-username/ADS-Trading.git
    cd ADS-Trading
    ```

2.  **安装依赖** (推荐使用虚拟环境)
    ```bash
    pip install -r requirements.txt
    ```

### 五分钟上手：运行你的第一个回测

我们提供了一个简单的移动平均线策略示例。

```python
# examples/quickstart.py
import pandas as pd
from ads_core.data_handler import DataHandler
from ads_core.backtest.vectorized_engine import VectorBacktest
from ads_analytics.performance import create_report

# 1. 准备数据 (这里用随机数据示例)
data = pd.DataFrame({
    'close': ... # 你的价格数据
})

# 2. 定义你的策略
class MovingAverageCrossStrategy:
    def __init__(self, short_window=10, long_window=30):
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, data):
        # 策略逻辑
        data['short_ma'] = data['close'].rolling(self.short_window).mean()
        data['long_ma'] = data['close'].rolling(self.long_window).mean()
        data['signal'] = 0
        data.loc[data['short_ma'] > data['long_ma'], 'signal'] = 1
        data.loc[data['short_ma'] < data['long_ma'], 'signal'] = -1
        return data

# 3. 运行回测
strategy = MovingAverageCrossStrategy()
result = strategy.generate_signals(data.copy())

# 4. 在回测引擎中分析
backtest = VectorBacktest()
portfolio = backtest.run(result, data['close'])

# 5. 生成报告
create_report(portfolio)
print("回测完成！请查看生成的报告。")
