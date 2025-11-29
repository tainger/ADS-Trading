"""
    爬取bitmex交易所数据

    XBTUSD
    XBTU19
    XBTZ19  6/15号开始.
"""
import os
import datetime
import time
import pandas as pd
import ccxt

pd.set_option('expand_frame_repr', False)

BITFINEX_LIMIT = 5000
BITMEX_LIMIT = 500
BINANCE_LIMIT = 500

# 代理设置示例
# 如果需要使用代理，可以取消下面的注释并配置您的代理地址
PROXY = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890'
}

# 测试代理配置
if PROXY:
    binance = ccxt.binance({
        'proxies': PROXY
    })
    print("使用代理连接到Binance")
else:
    binance = ccxt.binance()
    print("不使用代理连接到Binance")

try:
    binance.load_markets()
    print(f"成功连接到Binance，可用交易对数量：{len(binance.symbols)}")
    print("部分交易对示例：", binance.symbols[:5])
except Exception as e:
    print(f"连接Binance失败：{e}")


def crawl_exchanges_datas(exchange_name, symbol, start_time, end_time, proxy=None):
    """
    爬取交易所数据的方法.
    :param exchange_name:  交易所名称.
    :param symbol: 请求的symbol: like BTC/USDT, ETH/USD等。
    :param start_time: like 2018-1-1
    :param end_time: like 2019-1-1
    :param proxy: 代理设置字典，格式: {'http': 'http://ip:port', 'https': 'http://ip:port'}
    :return:
    """

    # 交易所配置
    exchange_config = {
        'timeout': 30000,  # 30秒超时
        'enableRateLimit': True,  # 启用速率限制
    }

    # 添加代理配置
    if proxy:
        exchange_config['proxies'] = proxy

    exchange_class = getattr(ccxt, exchange_name)   # 获取交易所的名称 ccxt.binance
    exchange = exchange_class(exchange_config)  # 交易所的类. 类似 ccxt.bitfinex()
    print(f"交易所配置: {exchange_config}")

    current_path = os.getcwd()
    file_dir = os.path.join(current_path, exchange_name, symbol.replace('/', ''))

    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d')
    end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d')

    start_time_stamp = int(time.mktime(start_time.timetuple())) * 1000
    end_time_stamp = int(time.mktime(end_time.timetuple())) * 1000

    print(f"开始时间戳: {start_time_stamp}")
    print(f"结束时间戳: {end_time_stamp}")

    limit_count = 500
    if exchange_name == 'bitfinex':
        limit_count = BITFINEX_LIMIT
    elif exchange_name == 'bitmex':
        limit_count = BITMEX_LIMIT
    elif exchange_name == 'binance':
        limit_count = BINANCE_LIMIT

    while True:
        try:
            print(f"正在请求数据，起始时间: {start_time_stamp}")
            data = exchange.fetch_ohlcv(symbol, timeframe='1m', since=start_time_stamp, limit=limit_count)

            if not data:
                print("未获取到数据，可能已到达最新数据")
                break

            df = pd.DataFrame(data)
            df.rename(columns={0: 'open_time', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'}, inplace=True)

            print(f"获取到 {len(df)} 条数据")

            start_time_stamp = int(df.iloc[-1]['open_time'])  # 获取下一个次请求的时间.

            filename = str(start_time_stamp) + '.csv'
            save_file_path = os.path.join(file_dir, filename)

            print(f"文件保存路径为：{save_file_path}")
            df.set_index('open_time', drop=True, inplace=True)
            df.to_csv(save_file_path)

            if start_time_stamp > end_time_stamp:
                print("完成数据的请求.")
                break

            if len(df) < limit_count:
                print("数据量不够了")
                break

            time.sleep(3)

        except ccxt.NetworkError as network_error:
            print(f"网络错误: {network_error}")
            print("将在10秒后重试...")
            time.sleep(10)
        except ccxt.ExchangeError as exchange_error:
            print(f"交易所错误: {exchange_error}")
            print("将在10秒后重试...")
            time.sleep(10)
        except Exception as error:
            print(f"其他错误: {error}")
            print("将在10秒后重试...")
            time.sleep(10)


def sample_data_vnpy_data(exchange_name, symbol):
    path = os.path.join(os.getcwd(), exchange_name, symbol.replace('/', ''))
    print(f"the data path = {path}")

    file_paths = []
    for root, dirs, files in os.walk(path):
        if files:
            for file in files:
                if file.endswith('.csv'):
                    file_paths.append(os.path.join(path, file))

    file_paths = sorted(file_paths)
    all_df = pd.DataFrame()

    for file in file_paths:
        df = pd.read_csv(file)
        all_df = pd.concat([all_df, df], ignore_index=True)

    all_df = all_df.sort_values(by='open_time', ascending=True)

    df = all_df

    # df['open_time'] = df['open_time'].apply(lambda x: time.mktime(x.timetuple()))
    # # 日期.timetuple() 这个用法 通过它将日期转换成时间元组
    # # print(df)
    # df['open_time'] = df['open_time'].apply(lambda x: (x // 60) * 60 * 1000)

    df['open_time'] = df['open_time'].apply(lambda x: (x // 60) * 60)

    df['Datetime'] = pd.to_datetime(df['open_time'], unit='ms') + pd.Timedelta(hours=8)
    df.drop_duplicates(subset=['open_time'], inplace=True)
    # 2019-10-1 10:10:00
    df['Datetime'] = df['Datetime'].apply(lambda x: str(x)[0:19])
    df["high"] = df.apply(lambda x: max(x['open'], x['high'], x['low'], x['close']), axis=1)
    df["low"] = df.apply(lambda x: min(x['open'], x['high'], x['low'], x['close']), axis=1)
    df.set_index('Datetime', inplace=True)

    print("*" * 20)

    df.rename(columns={'open': 'Open', 'high': 'High',
                       'low': 'Low', 'close': 'Close', 'volume': 'Volume'},
              inplace=True)

    df.to_csv(path + '_vnpy.csv')
    print(f"数据已转换为VNPY格式并保存到: {path + '_vnpy.csv'}")

    print(df.head())

if __name__ == '__main__':
    # 使用代理示例（取消注释并配置您的代理）
    # proxy_config = {
    #     'http': 'http://127.0.0.1:7890',
    #     'https': 'http://127.0.0.1:7890'
    # }

    # 不使用代理
    proxy_config = PROXY

    # 爬取数据
    crawl_exchanges_datas('binance', 'BTCUSDT', '2024-11-20', '2024-11-21', proxy=proxy_config)

    # 转换为VNPY格式
    sample_data_vnpy_data('binance', 'BTCUSDT')

    """
    关于CCXT代理设置的说明：
    1. CCXT支持通过'proxies'参数设置HTTP/HTTPS代理
    2. 代理格式：{'http': 'http://ip:port', 'https': 'http://ip:port'}
    3. 通常HTTP和HTTPS可以使用相同的代理地址
    4. 常见的代理端口：7890（Clash/Shadowsocks）、1080（传统Socks5，需要转换为HTTP代理）
    5. 如果使用Socks5代理，需要先转换为HTTP代理（可以使用工具如privoxy）
    
    示例：
    proxy = {
        'http': 'http://127.0.0.1:7890',
        'https': 'http://127.0.0.1:7890'
    }
    
    使用方法：
    1. 取消上面的proxy_config注释
    2. 修改为您的代理地址和端口
    3. 运行脚本即可通过代理访问交易所API
    """



