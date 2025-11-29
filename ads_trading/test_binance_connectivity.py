#!/usr/bin/env python3
"""
币安API连通性测试脚本
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from trader.gateway.binance_gateway import BinanceGateway, BinanceGatewayConfig

def main():
    """主函数"""
    print("=== 币安API连通性测试 ===")
    
    # 使用用户提供的API密钥
    API_KEY = "nuOIPVcbx4PU2fwkR8qOhYtgHIBlshuCdRoOYXkVBrQgMAGPykXwXLWsum3sqbMW"
    API_SECRET = "JQDQWyGh6yzv8QYIi3fjypRE5aVCAgAvuMWmbSLEPqQbZs3XXA8YCKMr6ZpBmVjb"
    PROXY_PORT = 7890
    
    # 创建配置
    config = BinanceGatewayConfig(
        api_key=API_KEY,
        api_secret=API_SECRET,
        testnet=False,  # 设置为True使用测试网
        proxy_host="127.0.0.1",
        proxy_port=PROXY_PORT
    )
    
    # 创建网关实例
    gateway = BinanceGateway()
    
    try:
        # 连接到币安
        print("连接到币安API...")
        print(f"使用代理: {config.proxy_host}:{config.proxy_port}")
        print(f"API Key: {API_KEY[:10]}...")
        print(f"API Secret: {API_SECRET[:10]}...")
        
        # 直接使用ccxt测试连接
        import ccxt
        
        print("\n直接使用CCXT测试连接...")
        exchange = ccxt.binance({
            'apiKey': API_KEY,
            'secret': API_SECRET,
            'enableRateLimit': True,
            'timeout': 10000,
            'proxies': {
                'http': f'http://{config.proxy_host}:{config.proxy_port}',
                'https': f'http://{config.proxy_host}:{config.proxy_port}'
            }
        })
        
        # 测试获取服务器时间
        print("测试获取服务器时间...")
        server_time = exchange.fetch_time()
        print(f"✅ 服务器时间获取成功: {server_time}")
        
        print("\n使用网关连接...")
        
        # 直接检查gateway的connect方法实现
        print("检查网关配置...")
        
        # 先将配置应用到网关
        gateway.config = config
        
        print(f"网关API Key: {gateway.config.api_key[:10]}...")
        print(f"网关API Secret: {gateway.config.api_secret[:10]}...")
        print(f"网关代理: {gateway.config.proxy_host}:{gateway.config.proxy_port}")
        print(f"网关测试网: {gateway.config.testnet}")
        
        # 尝试连接并获取详细错误
        try:
            print("\n开始测试API连接...")
            
            # 首先创建一个不需要身份验证的交易所实例来测试基本连接
            public_exchange_config = {
                'enableRateLimit': True,
                'timeout': 10000
            }
            
            # 设置代理
            if gateway.config.proxy_host and gateway.config.proxy_port:
                public_exchange_config['proxies'] = {
                    'http': f'http://{gateway.config.proxy_host}:{gateway.config.proxy_port}',
                    'https': f'http://{gateway.config.proxy_host}:{gateway.config.proxy_port}'
                }
            
            print("测试公共API连接...")
            public_exchange = ccxt.binance(public_exchange_config)
            
            # 测试公共API（不需要身份验证）
            ticker = public_exchange.fetch_ticker('BTC/USDT')
            print(f"✅ 成功获取BTC/USDT行情: {ticker['last']}")
            
            # 获取服务器时间
            server_time = public_exchange.fetch_time()
            print(f"✅ 服务器时间: {server_time}")
            
            # 获取本地时间
            import time
            local_time = int(time.time() * 1000)
            print(f"本地时间: {local_time}")
            
            # 计算时间差
            time_diff = server_time - local_time
            print(f"时间差: {time_diff} ms")
            
            # 如果时间差太大，提示用户
            if abs(time_diff) > 5000:
                print(f"⚠️  警告: 本地时间与服务器时间差异较大 ({abs(time_diff)} ms)")
                print("   请确保本地系统时间准确")
            
            # 现在尝试使用API密钥测试身份验证
            print("\n测试API密钥身份验证...")
            
            # 打印详细的时间信息
            print(f"详细时间信息:")
            print(f"  服务器时间: {server_time}")
            print(f"  本地时间: {local_time}")
            print(f"  时间差: {server_time - local_time} ms")
            print(f"  时间差(秒): {(server_time - local_time) / 1000} s")
            
            # 尝试直接使用服务器时间来生成请求
            print("\n尝试直接使用服务器时间生成请求...")
            
            # 保存原始的时间戳生成方法
            import time as time_module
            original_time = time_module.time
            
            try:
                # 重写time.time()函数，返回服务器时间（转换为秒）
                def mock_time():
                    return server_time / 1000
                
                # 替换原始的time.time()
                time_module.time = mock_time
                
                # 创建交易所实例
                auth_exchange = ccxt.binance({
                    'apiKey': gateway.config.api_key,
                    'secret': gateway.config.api_secret,
                    'enableRateLimit': True,
                    'timeout': 10000,
                    'recvWindow': 600000,  # 10分钟的接收窗口
                    'proxies': public_exchange_config['proxies'] if 'proxies' in public_exchange_config else None
                })
                
                # 关闭自动时间调整，因为我们已经在使用服务器时间
                auth_exchange.options['adjustForTimeDifference'] = False
                
                # 尝试获取账户信息
                print("使用服务器时间尝试获取账户余额...")
                balance = auth_exchange.fetch_balance()
                print(f"✅ 成功获取账户余额信息")
                
                # 显示账户余额
                print("\n📊 账户余额:")
                if balance['total']:
                    has_balance = False
                    for currency, amount in balance['total'].items():
                        if amount > 0.00000001:  # 只显示有余额的货币
                            print(f"  {currency}: {amount}")
                            has_balance = True
                    if not has_balance:
                        print("  暂无可用余额")
                else:
                    print("  暂无可用余额")
                
                print("\n🎉 币安API连通性测试成功！")
                print("\n📋 测试结果总结:")
                print("✅ 网络连接正常")
                print("✅ 代理设置正确")
                print("✅ API密钥格式有效")
                print("✅ 身份验证成功")
                print("✅ 账户信息获取成功")
                print(f"✅ 解决了时间差问题 ({(server_time - local_time) / 1000} s)")
                success = True
            except Exception as auth_e:
                print(f"⚠️  身份验证请求失败: {auth_e}")
                print("   这可能是由于API密钥权限不足或其他问题导致的")
                print("   但公共API测试成功，说明网络和代理设置正常")
                
                # 打印API密钥信息
                print(f"API密钥长度: {len(gateway.config.api_key)}, 密钥长度: {len(gateway.config.api_secret)}")
                
                # 测试API密钥格式
                try:
                    import hmac
                    import hashlib
                    
                    # 尝试使用API密钥和密钥生成签名，验证格式是否正确
                    test_params = {'timestamp': server_time}
                    query_string = '&'.join([f"{k}={v}" for k, v in test_params.items()])
                    signature = hmac.new(
                        gateway.config.api_secret.encode('utf-8'),
                        query_string.encode('utf-8'),
                        hashlib.sha256
                    ).hexdigest()
                    
                    print(f"✅ API密钥和密钥可以生成有效的HMAC签名")
                    print(f"   签名示例: {signature[:20]}...")
                except Exception as sign_e:
                    print(f"❌ 无法使用API密钥和密钥生成有效签名: {sign_e}")
                
                print("\n建议检查:")
                print("1. API密钥是否有足够的权限（至少需要读取账户信息权限）")
                print("2. API密钥是否已正确启用")
                print("3. 是否在币安官网添加了当前IP地址到白名单")
                
                success = False
            finally:
                # 恢复原始的time.time()函数
                time_module.time = original_time
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            import traceback
            traceback.print_exc()
            success = False
        
        if not success:
            print("\n请检查:")
            print("1. API密钥和密钥是否正确")
            print("2. 网络连接是否正常")
            print("3. 代理设置是否正确")
            print("4. 币安API是否可用")
            print("5. 本地系统时间是否准确")
            print("6. API密钥是否有足够的权限")
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭网关连接
        gateway.close()
        print("\n👋 测试结束")

if __name__ == "__main__":
    main()
