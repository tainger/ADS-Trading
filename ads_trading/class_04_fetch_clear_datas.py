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

binance = ccxt.binance()
binance.load_markets()
print(binance.symbols)


def crawl_exchanges_datas(exchange_name, symbol, start_time, end_time):
    """
    爬取交易所数据的方法.
    :param exchange_name:  交易所名称.
    :param symbol: 请求的symbol: like BTC/USDT, ETH/USD等。
    :param start_time: like 2018-1-1
    :param end_time: like 2019-1-1
    :return:
    """

    exchange_class = getattr(ccxt, exchange_name)   # 获取交易所的名称 ccxt.binance
    exchange = exchange_class()  # 交易所的类. 类似 ccxt.bitfinex()
    print(exchange)
    # exit()

    current_path = os.getcwd()
    file_dir = os.path.join(current_path, exchange_name, symbol.replace('/', ''))

    if not os.path.exists(file_dir):
        os.makedirs(file_dir)


    start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d')
    end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d')

    start_time_stamp = int(time.mktime(start_time.timetuple())) * 1000
    end_time_stamp = int(time.mktime(end_time.timetuple())) * 1000

    print(start_time_stamp)  # 1529233920000
    print(end_time_stamp)

    limit_count = 500
    if exchange_name == 'bitfinex':
        limit_count = BITFINEX_LIMIT
    elif exchange_name == 'bitmex':
        limit_count = BITMEX_LIMIT
    elif exchange_name == 'binance':
        limit_count = BINANCE_LIMIT

    while True:
        try:

            print(start_time_stamp)
            data = exchange.fetch_ohlcv(symbol, timeframe='1m', since=start_time_stamp, limit=limit_count)
            df = pd.DataFrame(data)

            df.rename(columns={0: 'open_time', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'}, inplace=True)

            print(df)

            start_time_stamp = int(df.iloc[-1]['open_time'])  # 获取下一个次请求的时间.

            filename = str(start_time_stamp) + '.csv'
            save_file_path = os.path.join(file_dir, filename)

            print("文件保存路径为：%s" % save_file_path)
            # exit()
            df.set_index('open_time', drop=True, inplace=True)
            df.to_csv(save_file_path)

            if start_time_stamp > end_time_stamp:
                print("完成数据的请求.")
                break

            if len(df) < limit_count:
                print("数据量不够了")
                break

            time.sleep(3)

        except Exception as error:
            print(error)
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
        all_df = all_df.append(df, ignore_index=True)

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

    print(df)

if __name__ == '__main__':
    crawl_exchanges_datas('binance', 'BTCUSDT', '2024-11-20', '2025-4-28')
    sample_data_vnpy_data('binance', 'BTCUSDT')

    # symbol = "BTC/USDT"
    # crawl_exchanges_datas("binance", symbol, "2017-8-1", "2019-11-14")

    # sample_data_vnpy_data('binance', 'ETH/USDT')
    # sample_data_vnpy_data('binance', 'BTC/USDT')
    # sample_data_vnpy_data('bitmex', 'BTC/USD')


