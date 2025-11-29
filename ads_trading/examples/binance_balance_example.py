#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
币安账户余额查询示例
"""

import sys
import os

# 将项目根目录添加到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trader.gateway.binance_gateway import BinanceGateway, BinanceGatewayConfig

def main():
    """主函数"""
    # 1. 创建币安网关实例
    binance_gateway = BinanceGateway()
    
    # 2. 配置币安网关
    # 注意：实际使用时，这些配置应该从安全的地方加载，而不是硬编码
    config = BinanceGatewayConfig(
        api_key="your_api_key",
        api_secret="your_api_secret",
        passphrase="your_passphrase",  # 仅期货API需要
        testnet=False,  # 是否使用测试网
        proxy_host=None,  # 代理主机
        proxy_port=None  # 代理端口
    )
    
    # 3. 连接到币安API
    print("正在连接币安API...")
    if not binance_gateway.connect(config):
        print("连接失败，程序退出")
        return
    
    print("连接成功！")
    
    # 4. 查询账户余额
    print("\n=== 查询账户余额 ===")
    
    # 4.1 查询现货账户余额
    print("\n1. 现货账户余额：")
    spot_balance = binance_gateway.get_spot_balance()
    if spot_balance:
        for currency, balance in spot_balance.items():
            print(f"   {currency}: {balance}")
    else:
        print("   未查询到现货账户余额")
    
    # 4.2 查询合约账户余额
    print("\n2. 合约账户余额：")
    futures_balance = binance_gateway.get_futures_balance()
    if futures_balance:
        for currency, balance in futures_balance.items():
            print(f"   {currency}: {balance}")
    else:
        print("   未查询到合约账户余额")
    
    # 4.3 查询总账户余额
    print("\n3. 总账户余额（USDT）：")
    total_balance = binance_gateway.get_total_balance()
    print(f"   {total_balance} USDT")
    
    # 4.4 查询所有账户余额（详细）
    print("\n4. 所有账户余额（详细）：")
    all_balances = binance_gateway.get_all_balances()
    if all_balances:
        if 'spot' in all_balances:
            print("   现货账户：")
            spot = all_balances['spot']
            if 'total' in spot:
                for currency, balance in spot['total'].items():
                    if balance > 0:
                        print(f"     {currency}: {balance}")
        
        if 'future' in all_balances:
            print("   合约账户：")
            future = all_balances['future']
            if 'total' in future:
                for currency, balance in future['total'].items():
                    if balance > 0:
                        print(f"     {currency}: {balance}")
    else:
        print("   未查询到账户余额")
    
    # 5. 关闭网关连接
    binance_gateway.close()
    print("\n程序执行完成")

if __name__ == "__main__":
    main()
