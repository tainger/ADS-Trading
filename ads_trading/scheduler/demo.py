from apscheduler.schedulers.blocking import BlockingScheduler
import requests
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


API_URL = "https://fapi.binance.com/fapi/v1/exchangeInfo"

klines_url = "https://fapi.binance.com/fapi/v1/klines"

from datetime import datetime


def job1():
    print("每30秒执行一次")
    response = requests.get(API_URL, timeout=10)
    # 检查请求是否成功
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 数据获取成功！服务器时间：{datetime.fromtimestamp(data['serverTime'] / 1000)}")
        print(f"📊 时区：{data['timezone']}")
        print(f"📈 交易对总数：{len(data['symbols'])}")
        symbols = data['symbols']
        symbols_list = [symbol['symbol'] for symbol in symbols]
        print(f"前5个交易对：{symbols_list[:5]}")
        i = 0
        for symbol_info in symbols_list:
            i =  i + 1
            print(f"第{i}个交易你对")
            print(symbol_info)
            print("-----------查询4h突破级别-----------")
            params = {
                "symbol": symbol_info,
                "interval": "4h",
                "limit": 1500
            }
            # 发送GET请求
            response = requests.get(
                url=klines_url,
                params=params,
                timeout=30  # 设置超时时间
            )
            data = response.json()


            print(f"请求成功！获取到 {len(data)} 条K线数据")

            print("-----------查询日级别-----------")
            params = {
                "symbol": symbol_info,
                "interval": "1d",
                "limit": 1500
            }
            # 发送GET请求
            response = requests.get(
                url=klines_url,
                params=params,
                timeout=30  # 设置超时时间
            )

            print("------最近三年------最近二年------最近一年------最近四个月------最近一个月------最近一个星期------最近一天------")
            data = response.json()

            df = pd.DataFrame(data, columns=[
                'open_time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])

            # 转换时间戳和价格
            df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
            df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['close'] = df['close'].astype(float)

            # 按时间排序
            df = df.sort_values('open_time')

            # 3. 获取当前时间
            current_time = datetime.now()

            # 4. 定义时间范围
            time_ranges = {
                '最近一天': timedelta(days=1),
                '最近一个星期': timedelta(weeks=1),
                '最近一个月': timedelta(days=30),
                '最近四个月': timedelta(days=120),
                '最近一年': timedelta(days=365),
                '最近二年': timedelta(days=730),
                '最近三年': timedelta(days=1095)
            }

            results = []

            # 5. 为每个时间范围计算回撤
            for range_name, delta in time_ranges.items():
                # 筛选时间范围内的数据
                cutoff_time = current_time - delta
                mask = df['open_time'] >= cutoff_time
                period_df = df[mask]

                if len(period_df) == 0:
                    results.append({
                        '时间范围': range_name,
                        '起始时间': cutoff_time.strftime('%Y-%m-%d'),
                        '数据点数': 0,
                        '最高点': None,
                        '最高点时间': None,
                        '最低点': None,
                        '最低点时间': None,
                        '回撤幅度': None,
                        '当前价格': None,
                        '从最高点回撤': None
                    })
                    continue

                # 找到最高点和最低点
                max_price = period_df['high'].max()
                min_price = period_df['low'].min()
                current_price = period_df.iloc[-1]['close']

                # 找到对应的时间
                max_row = period_df.loc[period_df['high'].idxmax()]
                min_row = period_df.loc[period_df['low'].idxmin()]

                max_time = max_row['open_time']
                min_time = min_row['open_time']

                # 计算回撤（从最高点到最低点的跌幅）
                if max_price > 0:
                    # 整体回撤幅度（最高到最低）
                    total_retracement = ((max_price - min_price) / max_price) * 100

                    # 从最高点到当前价格的回撤
                    current_retracement_from_high = ((
                                                                 max_price - current_price) / max_price) * 100 if max_price > current_price else 0

                    # 从最低点到当前价格的涨幅
                    current_increase_from_low = ((current_price - min_price) / min_price) * 100 if min_price > 0 else 0
                else:
                    total_retracement = None
                    current_retracement_from_high = None
                    current_increase_from_low = None

                results.append({
                    '时间范围': range_name,
                    '起始时间': cutoff_time.strftime('%Y-%m-%d'),
                    '数据点数': len(period_df),
                    '最高点': round(max_price, 4),
                    '最高点时间': max_time.strftime('%Y-%m-%d'),
                    '最低点': round(min_price, 4),
                    '最低点时间': min_time.strftime('%Y-%m-%d'),
                    '最高到最低回撤': f"{round(total_retracement, 2)}%" if total_retracement else None,
                    '当前价格': round(current_price, 4),
                    '从最高点回撤': f"{round(current_retracement_from_high, 2)}%" if current_retracement_from_high is not None else None,
                    '从最低点上涨': f"{round(current_increase_from_low, 2)}%" if current_increase_from_low is not None else None
                })

            # 6. 创建结果DataFrame
            result_df = pd.DataFrame(results)

            # 7. 输出详细分析报告
            print("=" * 80)
            print(f"交易对: {symbol_info}")
            print(
                f"数据时间段: {df['open_time'].min().strftime('%Y-%m-%d')} 到 {df['open_time'].max().strftime('%Y-%m-%d')}")
            print(f"总数据点数: {len(df)}")
            print("=" * 80)

            # 打印统计表格
            print("\n不同时间范围回撤统计:")
            print("-" * 120)
            print(
                f"{'时间范围':<12} {'起始时间':<12} {'数据点':<6} {'最高点':<12} {'最高点时间':<12} {'最低点':<12} {'最低点时间':<12} {'回撤幅度':<12} {'当前价格':<12} {'从高点回撤':<12}")
            print("-" * 120)

            for _, row in result_df.iterrows():
                print(f"{row['时间范围']:<12} {row['起始时间']:<12} {row['数据点数']:<6} "
                      f"{str(row['最高点']):<12} {str(row['最高点时间']):<12} {str(row['最低点']):<12} {str(row['最低点时间']):<12} "
                      f"{str(row['最高到最低回撤']):<12} {str(row['当前价格']):<12} {str(row['从最高点回撤']):<12}")

            print("-" * 120)

            # 8. 输出关键洞察
            print("\n📊 关键洞察:")
            print("-" * 40)

            # 找到最大回撤的时间范围
            max_retracement_row = result_df.loc[result_df['最高到最低回撤'].notna()]
            if not max_retracement_row.empty:
                max_retracement_row = max_retracement_row.loc[
                    max_retracement_row['最高到最低回撤'].str.replace('%', '').astype(float).idxmax()
                ]
                print(
                    f"1. 最大回撤发生在 '{max_retracement_row['时间范围']}'，回撤幅度为 {max_retracement_row['最高到最低回撤']}")

            # 当前回撤状态
            latest_row = result_df.iloc[0]  # 最近一天的数据
            if latest_row['从最高点回撤']:
                current_retracement = float(latest_row['从最高点回撤'].replace('%', ''))
                if current_retracement > 20:
                    print(f"2. ⚠️  当前价格较近期高点回撤较大: {latest_row['从最高点回撤']}")
                elif current_retracement < 5:
                    print(f"2. ✅  当前价格接近近期高点，回撤仅: {latest_row['从最高点回撤']}")

            # 长期趋势分析
            three_year = result_df[result_df['时间范围'] == '最近三年'].iloc[0]
            one_year = result_df[result_df['时间范围'] == '最近一年'].iloc[0]

            if three_year['当前价格'] and one_year['当前价格']:
                three_year_price = three_year['当前价格']
                one_year_price = one_year['当前价格']

                if three_year_price and one_year_price:
                    long_term_change = ((one_year_price - three_year_price) / three_year_price) * 100
                    if long_term_change > 0:
                        print(f"3. 📈  长期趋势向上: 较3年前上涨 {long_term_change:.2f}%")
                    else:
                        print(f"3. 📉  长期趋势向下: 较3年前下跌 {abs(long_term_change):.2f}%")

            print("-----------{result_df}-----------{df}")
            print(f"请求成功！获取到 {len(data)} 条K线数据")
            print()
            print()

    else:
        print(f"❌ 请求失败，状态码：{response.status_code}")
        print(f"响应内容：{response.text[:200]}")  # 打印前200字符以便调试
        return None


def job2():
    print("每2小时执行一次")


def job3():
    print("每2小时执行一次")


# scheduler = BlockingScheduler()
#
# # 多种间隔设置
# scheduler.add_job(job1, 'interval', seconds= 2)
# scheduler.add_job(job3, 'interval', seconds=2)
# scheduler.add_job(job2, 'interval', hours=2)
# scheduler.add_job(job1, 'interval', minutes=5, seconds=10)  # 每5分10秒

# scheduler.start()
job1()