import logging
from typing import Dict, List, Optional
from logging import Logger, getLogger, INFO, StreamHandler
from dataclasses import dataclass

import ccxt
from ccxt.base.errors import NetworkError, ExchangeError

from ..constant import Exchange
from ..object import AccountData

@dataclass
class BinanceGatewayConfig:
    """币安网关配置"""
    api_key: str
    api_secret: str
    passphrase: Optional[str] = None
    testnet: bool = False
    proxy_host: Optional[str] = None
    proxy_port: Optional[int] = None

class BinanceGateway:
    """币安网关实现"""
    
    def __init__(self):
        """初始化币安网关"""
        self.gateway_name: str = "BINANCE"
        self.exchange: Optional[ccxt.binance] = None
        self.accounts: Dict[str, AccountData] = {}
        self.config: Optional[BinanceGatewayConfig] = None
        self.logger: Optional[Logger] = None
    
    def connect(self, config: BinanceGatewayConfig) -> bool:
        """连接到币安API"""
        self.config = config
        try:
            proxy_config = None
            if config.proxy_host and config.proxy_port:
                proxy_config = {
                    # HTTPS代理也使用http://前缀
                    'http': f'http://{config.proxy_host}:{config.proxy_port}',
                    'https': f'http://{config.proxy_host}:{config.proxy_port}'
                }
            
            # 先创建一个不需要身份验证的实例来获取服务器时间
            public_exchange = ccxt.binance({
                'enableRateLimit': True,
                'timeout': 10000,
                'proxies': proxy_config
            })
            
            # 获取服务器时间
            server_time = public_exchange.fetch_time()
            
            # 计算时间差
            import time
            local_time = int(time.time() * 1000)
            time_diff = server_time - local_time
            
            self.write_log(f"服务器时间: {server_time}, 本地时间: {local_time}, 时间差: {time_diff} ms")
            
            # 如果时间差超过5秒，使用时间同步修复
            if abs(time_diff) > 5000:
                self.write_log(f"检测到较大时间差 ({time_diff} ms)，启用时间同步修复")
            
            # 创建交易所实例
            self.exchange = ccxt.binance({
                'apiKey': config.api_key,
                'secret': config.api_secret,
                'enableRateLimit': True,
                'timeout': 10000,
                'recvWindow': 600000,  # 增加接收窗口到10分钟
                'proxies': proxy_config,
                'options': {
                    'adjustForTimeDifference': True,  # 自动调整时间差
                    'defaultType': 'spot'  # 默认使用现货
                }
            })
            
            # 设置测试网模式
            if config.testnet:
                self.exchange.set_sandbox_mode(True)
            
            # 测试连接
            self.exchange.fetch_balance()
            
            # 连接成功
            self.write_log("币安网关连接成功")
            return True
        except Exception as e:
            self.write_log(f"币安网关连接失败: {str(e)}")
            return False
    
    def get_all_balances(self) -> Dict[str, Dict[str, float]]:
        """获取所有账户余额"""
        if not self.exchange:
            self.write_log("币安网关未连接")
            return {}
        
        try:
            # 获取现货账户余额
            spot_balance = self.exchange.fetch_balance(params={'type': 'spot'})
            
            # 获取合约账户余额
            futures_balance = self.exchange.fetch_balance(params={'type': 'future'})
            
            # 获取总账户余额
            total_balance = {
                'spot': spot_balance,
                'future': futures_balance
            }
            
            self.write_log("成功获取币安账户余额")
            return total_balance
        except Exception as e:
            self.write_log(f"获取币安账户余额失败: {str(e)}")
            return {}
    
    def get_spot_balance(self) -> Dict[str, float]:
        """获取现货账户余额"""
        if not self.exchange:
            self.write_log("币安网关未连接")
            return {}
        
        try:
            balance = self.exchange.fetch_balance(params={'type': 'spot'})
            result = {}
            for currency, info in balance['total'].items():
                if info > 0:
                    result[currency] = info
            
            return result
        except Exception as e:
            self.write_log(f"获取现货账户余额失败: {str(e)}")
            return {}
    
    def get_futures_balance(self) -> Dict[str, float]:
        """获取合约账户余额"""
        if not self.exchange:
            self.write_log("币安网关未连接")
            return {}
        
        try:
            balance = self.exchange.fetch_balance(params={'type': 'future'})
            result = {}
            for currency, info in balance['total'].items():
                if info > 0:
                    result[currency] = info
            
            return result
        except Exception as e:
            self.write_log(f"获取合约账户余额失败: {str(e)}")
            return {}
    
    def get_total_balance(self, quote_currency: str = 'USDT') -> float:
        """获取总账户余额"""
        if not self.exchange:
            self.write_log("币安网关未连接")
            return 0.0
        
        try:
            # 获取现货和合约余额
            spot_balance = self.get_spot_balance()
            futures_balance = self.get_futures_balance()
            
            # 计算总余额
            total = 0.0
            
            # 处理现货余额
            if quote_currency in spot_balance:
                total += spot_balance[quote_currency]
            
            # 处理合约余额
            if quote_currency in futures_balance:
                total += futures_balance[quote_currency]
            
            return total
        except Exception as e:
            self.write_log(f"获取总账户余额失败: {str(e)}")
            return 0.0
    
    def write_log(self, msg: str, level: int = INFO):
        """记录日志"""
        if not self.logger:
            self.logger = getLogger(self.gateway_name)
            
        # 确保logger有处理器
        if not self.logger.handlers:
            from ..utility import log_formatter
            handler = logging.StreamHandler()
            handler.setFormatter(log_formatter)
            self.logger.addHandler(handler)
            
        # 记录日志
        self.logger.log(level, f"[{self.gateway_name}] {msg}")
    
    def close(self):
        """关闭网关连接"""
        self.write_log("币安网关已关闭")
