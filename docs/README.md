# ADS Trading 系统文档

ADS Trading是一个现代化的量化交易系统，采用Python + React架构，支持策略开发、回测和实盘交易。

## 项目特性

### 核心功能
- **策略框架**: 基于事件驱动的策略开发框架
- **回测系统**: 高效的历史数据回测引擎
- **实盘接口**: 可扩展的交易网关接口
- **数据管理**: 多数据库支持（SQLite、MySQL、MongoDB）
- **可视化界面**: 现代化的Web UI，支持桌面和移动端

### 技术架构
- **后端**: Python 3.10+, FastAPI
- **前端**: React 18, Chart.js
- **数据库**: SQLite, MySQL, MongoDB
- **ORM**: Peewee (SQL数据库), PyMongo (MongoDB)

## 目录结构

```
ADS-Trading/
├── ads_trading/              # 主源码目录
│   ├── trader/              # 交易核心模块
│   │   ├── backtest.py      # 回测引擎
│   │   ├── constant.py      # 常量定义
│   │   ├── datafeed/        # 数据源模块
│   │   ├── dbconnectors/    # 数据库连接器
│   │   ├── engine.py        # 交易引擎
│   │   ├── gateway/         # 交易网关
│   │   ├── object.py        # 核心对象
│   │   └── utility.py       # 工具函数
│   ├── web_ui/              # Web服务模块
│   └── main.py              # 系统入口
├── docs/                    # 文档目录
├── tests/                   # 测试用例
└── web-ui/                  # 前端项目
```

## 快速开始

### 安装依赖

#### 后端依赖
```bash
cd ads_trading
pip install -r requirements.txt
```

#### 前端依赖
```bash
cd web-ui
npm install
```

### 启动系统

#### 启动后端服务
```bash
cd ads_trading
python main.py
```

#### 启动前端服务
```bash
cd web-ui
npm start
```

### 访问界面

打开浏览器访问: `http://localhost:3000`

## 核心概念

### 1. 事件驱动架构

ADS Trading采用事件驱动架构，主要事件包括：
- `TickEvent`: 行情数据事件
- `BarEvent`: K线数据事件
- `OrderEvent`: 订单事件
- `TradeEvent`: 成交事件
- `PositionEvent`: 持仓变化事件

### 2. 策略开发

策略类需继承自`BaseStrategy`，实现以下方法：

```python
class MyStrategy(BaseStrategy):
    def on_init(self):
        # 策略初始化
        pass
    
    def on_tick(self, tick):
        # 处理行情事件
        pass
    
    def on_bar(self, bar):
        # 处理K线事件
        pass
    
    def on_trade(self, trade):
        # 处理成交事件
        pass
```

### 3. 回测系统

回测引擎支持：
- 多品种同时回测
- 任意时间周期（分钟、小时、日等）
- 详细的性能分析报告
- 可视化回测结果

### 4. 实盘交易

系统提供：
- 模拟交易网关（SimGateway）
- 可扩展的交易所接口
- 订单管理和风险控制
- 实时监控和告警

## 策略开发指南

### 创建策略文件

在`trader/strategy`目录下创建策略文件：

```python
# trader/strategy/moving_average.py
from trader.strategy import BaseStrategy
from trader.object import BarData, OrderData, TradeData
from trader.constant import Interval
from trader.utility import ArrayManager

class MovingAverageStrategy(BaseStrategy):
    