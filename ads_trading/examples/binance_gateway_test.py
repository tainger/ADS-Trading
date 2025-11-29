#!/usr/bin/env python3
"""
币安网关测试脚本
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trader.gateway.binance_gateway import BinanceGateway, BinanceGatewayConfig

def main():
    """主函数"""
    print("=== 币安网关测试 ===")
    
    # 从环境变量获取API密钥（推荐）或直接填写
    api_key = os.environ.get("BINANCE_API_KEY", "your_api_key")
    api_secret = os.environ.get("BINANCE_API_SECRET", "your_api_secret")
    
    # 创建配置
    config = BinanceGatewayConfig(
        api_key=api_key,
        api_secret=api_secret,
        testnet=False  # 设置为True使用测试网
    )
    
    # 创建网关实例
    gateway = BinanceGateway()
    
    try:
        # 连接到币安
        print("连接到币安API...")
        if gateway.connect(config):
            print("✅ 币安网关连接成功")
            
            # 获取现货账户余额
            print("\n📊 获取现货账户余额...")
            spot_balance = gateway.get_spot_balance()
            print("现货账户余额:")
            for currency, amount in spot_balance.items():
                if amount > 0:  # 只显示有余额的货币
                    print(f"  {currency}: {amount}")
            
            # 获取合约账户余额
            print("\n📊 获取合约账户余额...")
            futures_balance = gateway.get_futures_balance()
            print("合约账户余额:")
            for currency, amount in futures_balance.items():
                if amount > 0:  # 只显示有余额的货币
                    print(f"  {currency}: {amount}")
            
            # 获取总账户余额
            print("\n📊 获取总账户余额...")
            total = gateway.get_total_balance("USDT")
            print(f"总账户余额 (USDT): {total}")
            
            # 获取所有账户余额
            print("\n📊 获取所有账户余额...")
            all_balances = gateway.get_all_balances()
            print("所有账户余额:")
            print(f"  现货账户: {all_balances.get('spot', {}).get('total', {})}")
            print(f"  合约账户: {all_balances.get('future', {}).get('total', {})}")
        else:
            print("❌ 币安网关连接失败")
    except Exception as e:
        print(f"❌ 发生错误: {e}")
    finally:
        # 关闭网关连接
        gateway.close()
        print("\n👋 测试结束")

if __name__ == "__main__":
    main()
