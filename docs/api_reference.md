# ADS Trading API参考

本文档提供了ADS Trading量化交易系统的核心API参考，包括主要类、方法和接口的详细说明。

## 1. 核心模块

### 1.1 Engine模块

Engine是系统的核心引擎，负责协调各个组件的工作。

#### TraderEngine类

```python
from trader.engine import TraderEngine
```

**主要方法：**

- `__init__(self, setting)`：初始化引擎
- `start(self)`：启动引擎
- `stop(self)`：停止引擎
- `register_strategy(self, strategy_class, setting)`：注册策略
- `subscribe(self, symbol, interval)`：订阅行情数据
- `send_order(self, order_data)`：发送订单
- `cancel_order(self, order_id)`：取消订单
- `get_account(self)`：获取账户信息
- `get_position(self, symbol)`：获取持仓信息
- `get_orders(self, symbol=None)`：获取订单列表
- `get_trades(self, symbol=None)`：获取成交列表

#### BacktestEngine类

```python
from trader.backtest import BacktestEngine
```

**主要方法：**

- `__init__(self)`：初始化回测引擎
- `set_parameters(self, strategy, symbol, interval, start, end, initial_capital=10000, slippage=0.001, commission=0.0002)`：设置回测参数
- `load_data(self, data_path=None)`：加载历史数据
- `run(self)`：运行回测
- `get_results(self)`：获取回测结果
- `plot_results(self)`：绘制回测结果图表

## 2. 策略开发API

### 2.1 BaseStrategy类

所有策略都必须继承自BaseStrategy类。

```python
from trader.strategy import BaseStrategy
```

**主要方法：**

- `__init__(self, engine, setting=None)`：初始化策略
- `on_init(self)`：策略初始化回调
- `on_start(self)`：策略启动回调
- `on_stop(self)`：策略停止回调
- `on_tick(self, tick)`：处理Tick数据
- `on_bar(self, bar)`：处理Bar数据
- `on_order(self, order)`：处理订单事件
- `on_trade(self, trade)`：处理成交事件
- `on_position(self, position)`：处理持仓更新
- `on_account(self, account)`：处理账户更新
- `buy(self, symbol, price, volume, order_type="limit")`：买入
- `sell(self, symbol, price, volume, order_type="limit")`：卖出
- `short(self, symbol, price, volume, order_type="limit")`：做空
- `cover(self, symbol, price, volume, order_type="limit")`：平空
- `cancel_order(self, order_id)`：取消订单
- `request_bar_history(self, symbol, interval, size)`：请求历史K线数据
- `write_log(self, msg, level="INFO")`：写入日志

## 3. 数据结构

### 3.1 TickData

```python
from trader.object import TickData
```

**属性：**

- `symbol`：交易对代码
- `datetime`：时间戳
- `open_price`：开盘价
- `high_price`：最高价
- `low_price`：最低价
- `last_price`：最新价
- `volume`：成交量
- `amount`：成交额
- `bid_price_1`：买一价
- `bid_volume_1`：买一量
- `ask_price_1`：卖一价
- `ask_volume_1`：卖一量
- `bid_price_2`：买二价
- `bid_volume_2`：买二量
- `ask_price_2`：卖二价
- `ask_volume_2`：卖二量
- `bid_price_3`：买三价
- `bid_volume_3`：买三量
- `ask_price_3`：卖三价
- `ask_volume_3`：卖三量

### 3.2 BarData

```python
from trader.object import BarData
```

**属性：**

- `symbol`：交易对代码
- `datetime`：时间戳
- `interval`：周期
- `open_price`：开盘价
- `high_price`：最高价
- `low_price`：最低价
- `close_price`：收盘价
- `volume`：成交量
- `amount`：成交额

### 3.3 OrderData

```python
from trader.object import OrderData
```

**属性：**

- `order_id`：订单ID
- `symbol`：交易对代码
- `direction`：方向（"buy"/"sell"）
- `order_type`：订单类型（"limit"/"market"/"stop"）
- `price`：价格
- `volume`：数量
- `traded`：已成交数量
- `status`：状态（"submitted"/"filled"/"canceled"/"rejected"/"pending"）
- `datetime`：订单时间

### 3.4 TradeData

```python
from trader.object import TradeData
```

**属性：**

- `trade_id`：成交ID
- `order_id`：订单ID
- `symbol`：交易对代码
- `direction`：方向（"buy"/"sell"）
- `price`：成交价格
- `quantity`：成交数量
- `datetime`：成交时间
- `commission`：手续费

### 3.5 PositionData

```python
from trader.object import PositionData
```

**属性：**

- `symbol`：交易对代码
- `direction`：持仓方向（"long"/"short"）
- `quantity`：持仓数量
- `frozen`：冻结数量
- `price`：持仓均价
- `pnl`：浮动盈亏
- `datetime`：更新时间

### 3.6 AccountData

```python
from trader.object import AccountData
```

**属性：**

- `account_id`：账户ID
- `balance`：账户余额
- `frozen`：冻结资金
- `available`：可用资金
- `pnl`：总盈亏
- `datetime`：更新时间

## 4. 网关API

### 4.1 BaseGateway类

所有交易网关都必须继承自BaseGateway类。

```python
from trader.gateway.base_gateway import BaseGateway
```

**主要方法：**

- `__init__(self, gateway_name)`：初始化网关
- `connect(self)`：连接交易所
- `disconnect(self)`：断开连接
- `send_order(self, order_data)`：发送订单
- `cancel_order(self, order_id)`：取消订单
- `get_account(self)`：获取账户信息
- `get_position(self, symbol)`：获取持仓信息
- `get_orders(self, symbol=None)`：获取订单列表
- `get_trades(self, symbol=None)`：获取成交列表
- `subscribe(self, symbol, interval)`：订阅行情

### 4.2 SimGateway类

模拟交易网关，用于回测和策略测试。

```python
from trader.gateway.sim_gateway import SimGateway
```

**主要方法：**

继承自BaseGateway类，实现了模拟交易功能。

## 5. 工具模块

### 5.1 ArrayManager类

K线数据管理工具，用于计算各种技术指标。

```python
from trader.utility import ArrayManager
```

**主要方法：**

- `__init__(self, size=100)`：初始化数据管理器
- `update_bar(self, bar)`：更新K线数据
- `sma(self, n)`：计算简单移动平均线
- `ema(self, n)`：计算指数移动平均线
- `wma(self, n)`：计算加权移动平均线
- `rsi(self, n)`：计算相对强弱指标
- `macd(self, fast_period=12, slow_period=26, signal_period=9)`：计算MACD指标
- `boll(self, n, dev=2)`：计算布林带
- `kdj(self, n=9, m1=3, m2=3)`：计算KDJ指标
- `atr(self, n=14)`：计算平均真实波动幅度
- `cci(self, n=14)`：计算顺势指标
- `dmi(self, n=14)`：计算动向指标
- `obv(self)`：计算能量潮指标

### 5.2 Utility函数

```python
from trader.utility import *
```

**主要函数：**

- `round_to_pricescale(value, price_scale)`：按价格精度四舍五入
- `extract_vt_symbol(vt_symbol)`：解析vt_symbol
- `generate_vt_symbol(symbol, exchange)`：生成vt_symbol
- `get_exchange_from_vt_symbol(vt_symbol)`：从vt_symbol获取交易所
- `get_symbol_from_vt_symbol(vt_symbol)`：从vt_symbol获取交易对
- `load_json(filename)`：加载JSON文件
- `save_json(filename, data)`：保存JSON文件
- `load_csv(filename)`：加载CSV文件
- `save_csv(filename, data, headers=None)`：保存CSV文件
- `get_folder_path(folder_name)`：获取文件夹路径
- `get_file_path(filename)`：获取文件路径

## 6. 数据模块

### 6.1 BaseDataFeed类

所有数据源都必须继承自BaseDataFeed类。

```python
from trader.data import BaseDataFeed
```

**主要方法：**

- `__init__(self)`：初始化数据源
- `connect(self)`：连接数据源
- `disconnect(self)`：断开连接
- `subscribe(self, symbol, interval)`：订阅行情
- `get_bar_history(self, symbol, interval, start, end)`：获取历史K线数据

### 6.2 BinanceDataFeed类

币安交易所数据源。

```python
from trader.data.binance_data_feed import BinanceDataFeed
```

**主要方法：**

继承自BaseDataFeed类，实现了币安API的数据获取功能。

## 7. Web API

ADS Trading提供了RESTful API接口，用于与Web UI或其他应用程序交互。

### 7.1 市场数据API

- `GET /api/market`：获取市场数据概览
- `GET /api/market/{symbol}/ticks`：获取实时Tick数据
- `GET /api/market/{symbol}/bars/{interval}`：获取K线数据
- `GET /api/market/{symbol}/history`：获取历史价格数据

### 7.2 交易API

- `POST /api/orders`：提交订单
- `DELETE /api/orders/{order_id}`：取消订单
- `GET /api/orders`：获取订单列表
- `GET /api/orders/{order_id}`：获取订单详情

### 7.3 账户API

- `GET /api/account`：获取账户信息
- `GET /api/positions`：获取持仓列表
- `GET /api/positions/{symbol}`：获取持仓详情

### 7.4 历史API

- `GET /api/trades`：获取成交列表
- `GET /api/history`：获取历史交易记录

### 7.5 策略API

- `GET /api/strategies`：获取策略列表
- `GET /api/strategies/{name}`：获取策略详情
- `POST /api/strategies/{name}/start`：启动策略
- `POST /api/strategies/{name}/stop`：停止策略
- `PUT /api/strategies/{name}/params`：更新策略参数

## 8. 事件系统

### 8.1 EventEngine类

事件引擎，用于处理系统内的各种事件。

```python
from trader.event import EventEngine
```

**主要方法：**

- `__init__(self)`：初始化事件引擎
- `start(self)`：启动事件引擎
- `stop(self)`：停止事件引擎
- `register(self, event_type, handler)`：注册事件处理器
- `unregister(self, event_type, handler)`：注销事件处理器
- `put(self, event)`：发送事件

### 8.2 Event类

```python
from trader.event import Event
```

**属性：**

- `event_type`：事件类型
- `data`：事件数据

### 8.3 事件类型

预定义的事件类型：

- `EVENT_TICK`：Tick数据事件
- `EVENT_BAR`：Bar数据事件
- `EVENT_ORDER`：订单事件
- `EVENT_TRADE`：成交事件
- `EVENT_POSITION`：持仓事件
- `EVENT_ACCOUNT`：账户事件
- `EVENT_STRATEGY`：策略事件
- `EVENT_LOG`：日志事件

## 9. 日志模块

### 9.1 Logger类

```python
from trader.logger import Logger
```

**主要方法：**

- `__init__(self, name, level="INFO")`：初始化日志器
- `debug(self, msg)`：记录调试信息
- `info(self, msg)`：记录普通信息
- `warning(self, msg)`：记录警告信息
- `error(self, msg)`：记录错误信息
- `critical(self, msg)`：记录严重错误信息

## 10. 配置模块

### 10.1 Setting类

```python
from trader.setting import Setting
```

**主要方法：**

- `__init__(self, filename=None)`：初始化配置
- `get(self, key, default=None)`：获取配置项
- `set(self, key, value)`：设置配置项
- `load(self, filename)`：加载配置文件
- `save(self, filename)`：保存配置文件

---

本API参考提供了ADS Trading系统的核心组件和接口的详细说明。有关更多详细信息，请参考源代码和示例。
