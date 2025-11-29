# 币安网关使用指南

## 概述

本目录包含ADS Trading系统的币安网关实现，用于与币安交易所API交互，提供账户余额查询功能。

## 功能特性

- ✅ 币安API连接与认证
- ✅ 现货账户余额查询
- ✅ 合约账户余额查询
- ✅ 总账户余额统计
- ✅ 所有账户余额获取
- ✅ 日志记录功能

## 文件结构

```
├── binance_gateway.py    # 币安网关核心实现
├── __init__.py          # 模块导出
├── gateway_config.json  # 网关配置文件
└── README.md            # 本说明文件
```

## 安装依赖

确保已安装ccxt库：

```bash
pip install ccxt==4.5.22
```

## 配置与使用

### 1. 基本用法示例

```python
from trader.gateway.binance_gateway import BinanceGateway, BinanceGatewayConfig

# 创建配置
config = BinanceGatewayConfig(
    api_key="your_api_key",
    api_secret="your_api_secret",
    testnet=False  # 设置为True使用测试网
)

# 创建并连接网关
gateway = BinanceGateway()
gateway.connect(config)

# 获取现货账户余额
spot_balance = gateway.get_spot_balance()
print("现货账户余额:", spot_balance)

# 获取合约账户余额
futures_balance = gateway.get_futures_balance()
print("合约账户余额:", futures_balance)

# 获取总账户余额
total_balance = gateway.get_total_balance("USDT")
print("总账户余额 (USDT):", total_balance)

# 获取所有账户余额
all_balances = gateway.get_all_balances()
print("所有账户余额:", all_balances)

# 关闭网关
gateway.close()
```

### 2. 通过环境变量配置API密钥

```python
import os
from trader.gateway.binance_gateway import BinanceGateway, BinanceGatewayConfig

# 从环境变量获取API密钥（推荐）
api_key = os.environ.get("BINANCE_API_KEY", "")
api_secret = os.environ.get("BINANCE_API_SECRET", "")

# 创建配置
config = BinanceGatewayConfig(
    api_key=api_key,
    api_secret=api_secret,
    testnet=False
)

# 使用网关...
```

### 3. 配置代理

```python
config = BinanceGatewayConfig(
    api_key="your_api_key",
    api_secret="your_api_secret",
    proxy_host="127.0.0.1",
    proxy_port=7890
)
```

## 集成到MainEngine

由于MainEngine是从外部库howtrader导入的，您需要确保它能够加载我们的币安网关。以下是可能的集成方式：

### 方式一：通过配置文件加载

编辑`gateway_config.json`文件，添加币安网关配置：

```json
{
    "gateways": {
        "BINANCE": {
            "module": "trader.gateway.binance_gateway",
            "class": "BinanceGateway",
            "enabled": true,
            "api_key": "your_api_key",
            "api_secret": "your_api_secret",
            "testnet": false
        }
    }
}
```

### 方式二：手动注册网关

```python
from howtrader.trader.engine import MainEngine
from trader.gateway.binance_gateway import BinanceGateway, BinanceGatewayConfig

# 创建MainEngine实例
main_engine = MainEngine()

# 创建币安网关配置
config = BinanceGatewayConfig(
    api_key="your_api_key",
    api_secret="your_api_secret",
    testnet=False
)

# 创建并注册币安网关
binance_gateway = BinanceGateway()
main_engine.add_gateway(binance_gateway)

# 连接网关
main_engine.connect_gateway("BINANCE", config)

# 获取账户余额
accounts = main_engine.get_accounts("BINANCE")
print("币安账户余额:", accounts)
```

## API参考

### BinanceGatewayConfig

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
| api_key | str | 币安API密钥 | 必填 |
| api_secret | str | 币安API密钥密钥 | 必填 |
| passphrase | Optional[str] | API密码（现货账户） | None |
| testnet | bool | 是否使用测试网 | False |
| proxy_host | Optional[str] | 代理主机 | None |
| proxy_port | Optional[int] | 代理端口 | None |

### BinanceGateway

| 方法名 | 返回类型 | 描述 |
|--------|----------|------|
| connect(config: BinanceGatewayConfig) -> bool | bool | 连接到币安API |
| get_all_balances() -> Dict[str, Dict[str, float]] | Dict | 获取所有账户余额 |
| get_spot_balance() -> Dict[str, float] | Dict | 获取现货账户余额 |
| get_futures_balance() -> Dict[str, float] | Dict | 获取合约账户余额 |
| get_total_balance(quote_currency: str = 'USDT') -> float | float | 获取总账户余额 |
| write_log(msg: str, level: int = 20) | None | 记录日志 |
| close() | None | 关闭网关连接 |

## 示例

查看`examples`目录下的示例文件：

1. `binance_balance_example.py` - 基本的余额查询示例
2. `binance_gateway_test.py` - 完整的网关测试示例

运行示例：

```bash
# 设置API密钥环境变量
export BINANCE_API_KEY="your_api_key"
export BINANCE_API_SECRET="your_api_secret"

# 运行示例
python examples/binance_gateway_test.py
```

## 注意事项

1. **API密钥安全**：请不要将API密钥硬编码在代码中，建议使用环境变量或加密配置文件。
2. **API限制**：币安API有请求频率限制，请合理使用API。
3. **测试环境**：建议先在测试网(https://testnet.binance.vision/)测试代码，确保功能正常后再使用实网。
4. **权限设置**：创建API密钥时，请只授予必要的权限（如只读权限）。

## 故障排除

1. **连接失败**：检查API密钥是否正确，网络是否通畅，代理设置是否正确。
2. **余额查询失败**：检查API密钥是否有余额查询权限，网络是否稳定。
3. **日志记录**：查看日志输出，了解详细的错误信息。

## 版本历史

- v1.0.0 (2025-11-29): 初始版本，实现基本的币安网关功能
