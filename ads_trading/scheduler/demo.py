from apscheduler.schedulers.blocking import BlockingScheduler
import requests
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from ads_trading.trader.dbconnectors.sqlite_database import DBCoinAlphaFactor

API_URL = "https://fapi.binance.com/fapi/v1/exchangeInfo"
KLINES_URL = "https://fapi.binance.com/fapi/v1/klines"


def safe_strftime(date_obj, format_str='%Y-%m-%d', default='N/A'):
    """安全格式化时间，避免NaT错误"""
    if pd.isna(date_obj):
        return default
    try:
        return date_obj.strftime(format_str)
    except (AttributeError, ValueError):
        return default


def get_kline_data(symbol_info, interval="1d", limit=1500):
    """获取K线数据"""
    try:
        params = {
            "symbol": symbol_info,
            "interval": interval,
            "limit": limit
        }

        response = requests.get(
            url=KLINES_URL,
            params=params,
            timeout=30
        )

        if response.status_code != 200:
            print(f"❌ 获取{symbol_info}的{interval}K线数据失败: {response.status_code}")
            return None

        data = response.json()

        # 转换为DataFrame
        df = pd.DataFrame(data, columns=[
            'open_time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])

        # 转换时间戳和价格
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms', errors='coerce')
        df['close_time'] = pd.to_datetime(df['close_time'], unit='ms', errors='coerce')

        # 过滤掉时间戳为NaT的行
        df = df.dropna(subset=['open_time'])

        # 转换价格列
        price_columns = ['high', 'low', 'close', 'open']
        for col in price_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # 按时间排序
        df = df.sort_values('open_time')

        return df

    except Exception as e:
        print(f"❌ 处理{symbol_info}数据时出错: {e}")
        return None


def analyze_retracement(df, symbol_info, current_time=None):
    """分析回撤数据"""
    if df is None or len(df) == 0:
        print(f"⚠️  {symbol_info}: 无有效数据")
        return None

    if current_time is None:
        current_time = datetime.now()

    # 定义时间范围 - 添加了六个月、八个月、十个月
    time_ranges = {
        '最近一天': timedelta(days=1),
        '最近一个星期': timedelta(weeks=1),
        '最近一个月': timedelta(days=30),
        '最近四个月': timedelta(days=120),
        '最近六个月': timedelta(days=180),  # 新增
        '最近八个月': timedelta(days=240),  # 新增
        '最近十个月': timedelta(days=300),  # 新增
        '最近一年': timedelta(days=365),
        '最近二年': timedelta(days=730),
        '最近三年': timedelta(days=1095)
    }

    results = []

    for range_name, delta in time_ranges.items():
        cutoff_time = current_time - delta

        try:
            # 筛选时间范围内的数据
            mask = df['open_time'] >= cutoff_time
            period_df = df[mask]

            if len(period_df) == 0:
                results.append({
                    '时间范围': range_name,
                    '起始时间': safe_strftime(cutoff_time),
                    '数据点数': 0,
                    '最高点': None,
                    '最高点时间': None,
                    '最低点': None,
                    '最低点时间': None,
                    '最高到最低回撤': None,
                    '当前价格': None,
                    '从最高点回撤': None,
                    '从最低点上涨': None
                })
                continue

            # 找到最高点和最低点
            if period_df['high'].isna().all() or period_df['low'].isna().all():
                results.append({
                    '时间范围': range_name,
                    '起始时间': safe_strftime(cutoff_time),
                    '数据点数': len(period_df),
                    '最高点': None,
                    '最高点时间': None,
                    '最低点': None,
                    '最低点时间': None,
                    '最高到最低回撤': None,
                    '当前价格': None,
                    '从最高点回撤': None,
                    '从最低点上涨': None
                })
                continue

            max_price = period_df['high'].max()
            min_price = period_df['low'].min()
            current_price = period_df.iloc[-1]['close']

            # 找到对应的时间
            max_idx = period_df['high'].idxmax()
            min_idx = period_df['low'].idxmin()

            max_time = period_df.loc[max_idx, 'open_time']
            min_time = period_df.loc[min_idx, 'open_time']

            # 计算回撤
            if pd.isna(max_price) or max_price <= 0:
                total_retracement = None
                current_retracement_from_high = None
                current_increase_from_low = None
            else:
                # 整体回撤幅度（最高到最低）
                total_retracement = ((max_price - min_price) / max_price * 100) if not pd.isna(min_price) else None

                # 从最高点到当前价格的回撤
                if not pd.isna(current_price) and max_price > current_price:
                    current_retracement_from_high = ((max_price - current_price) / max_price * 100)
                else:
                    current_retracement_from_high = 0 if not pd.isna(current_price) else None

                # 从最低点到当前价格的涨幅
                if not pd.isna(min_price) and min_price > 0 and not pd.isna(current_price):
                    current_increase_from_low = ((current_price - min_price) / min_price * 100)
                else:
                    current_increase_from_low = None

            results.append({
                '时间范围': range_name,
                '起始时间': safe_strftime(cutoff_time),
                '数据点数': len(period_df),
                '最高点': round(max_price, 4) if not pd.isna(max_price) else None,
                '最高点时间': safe_strftime(max_time),
                '最低点': round(min_price, 4) if not pd.isna(min_price) else None,
                '最低点时间': safe_strftime(min_time),
                '最高到最低回撤': f"{round(total_retracement, 2)}%" if total_retracement is not None else None,
                '当前价格': round(current_price, 4) if not pd.isna(current_price) else None,
                '从最高点回撤': f"{round(current_retracement_from_high, 2)}%" if current_retracement_from_high is not None else None,
                '从最低点上涨': f"{round(current_increase_from_low, 2)}%" if current_increase_from_low is not None else None
            })

        except Exception as e:
            print(f"❌ 分析{range_name}时出错: {e}")
            continue

    return results


def print_analysis_report(symbol_info, results, df):
    """打印分析报告"""
    if not results or df is None or len(df) == 0:
        return

    print("=" * 100)
    print(f"📊 交易对: {symbol_info}")
    print(f"📅 数据时间段: {safe_strftime(df['open_time'].min())} 到 {safe_strftime(df['open_time'].max())}")
    print(f"📈 总数据点数: {len(df)}")
    print("=" * 100)

    # 打印统计表格 - 调整宽度以容纳更多列
    print("\n📋 不同时间范围回撤统计:")
    print("-" * 140)
    header = f"{'时间范围':<10} {'起始时间':<12} {'数据点':<6} {'最高点':<10} {'最高时间':<12} {'最低点':<10} {'最低时间':<12} {'最大回撤':<10} {'当前价':<10} {'高点回撤':<10}"
    print(header)
    print("-" * 140)

    for row in results:
        # 处理None值
        highest = str(row['最高点']) if row['最高点'] is not None else "N/A"
        lowest = str(row['最低点']) if row['最低点'] is not None else "N/A"
        max_retrace = str(row['最高到最低回撤']) if row['最高到最低回撤'] is not None else "N/A"
        current_price = str(row['当前价格']) if row['当前价格'] is not None else "N/A"
        from_high = str(row['从最高点回撤']) if row['从最高点回撤'] is not None else "N/A"

        print(f"{row['时间范围']:<10} "
              f"{row['起始时间']:<12} "
              f"{row['数据点数']:<6} "
              f"{highest:<10} "
              f"{str(row['最高点时间']):<12} "
              f"{lowest:<10} "
              f"{str(row['最低点时间']):<12} "
              f"{max_retrace:<10} "
              f"{current_price:<10} "
              f"{from_high:<10}")

    print("-" * 140)

    # 关键洞察
    print_key_insights(results)


def print_key_insights(results):
    """打印关键洞察"""
    if not results:
        return

    print("\n🔍 关键洞察:")
    print("-" * 40)

    # 重新排序结果以便分析
    # 定义分析顺序（从短期到长期）
    analysis_order = [
        '最近一天', '最近一个星期', '最近一个月',
        '最近四个月', '最近六个月', '最近八个月',
        '最近十个月', '最近一年', '最近二年', '最近三年'
    ]

    # 按顺序筛选结果
    ordered_results = []
    for time_range in analysis_order:
        for result in results:
            if result['时间范围'] == time_range:
                ordered_results.append(result)
                break

    if not ordered_results:
        return

    # 1. 分析各时间段的最大回撤
    valid_results = [r for r in ordered_results if r['最高到最低回撤'] is not None]
    if valid_results:
        # 找到最大回撤
        max_retracement = max(
            valid_results,
            key=lambda x: float(x['最高到最低回撤'].replace('%', '')) if x['最高到最低回撤'] and x[
                '最高到最低回撤'] != 'N/A' else 0
        )
        print(f"📉 最大回撤: '{max_retracement['时间范围']}'，幅度为 {max_retracement['最高到最低回撤']}")

        # 分析回撤趋势
        monthly_results = [r for r in ordered_results if '个月' in r['时间范围']]
        if len(monthly_results) >= 3:
            monthly_retracements = []
            for r in monthly_results:
                if r['最高到最低回撤'] and r['最高到最低回撤'] != 'N/A':
                    try:
                        monthly_retracements.append(float(r['最高到最低回撤'].replace('%', '')))
                    except:
                        pass

            if len(monthly_retracements) >= 3:
                # 检查回撤趋势
                if monthly_retracements[-1] > monthly_retracements[0]:
                    print(
                        f"📈 回撤趋势: 近期({monthly_results[-1]['时间范围']})回撤大于早期({monthly_results[0]['时间范围']})")
                else:
                    print(
                        f"📉 回撤趋势: 近期({monthly_results[-1]['时间范围']})回撤小于早期({monthly_results[0]['时间范围']})")

    # 2. 当前回撤状态（使用最近一个月的数据）
    monthly_results = [r for r in ordered_results if r['时间范围'] in ['最近一个月', '最近四个月', '最近六个月']]

    for monthly in monthly_results:
        if monthly and monthly['从最高点回撤'] and monthly['从最高点回撤'] != 'N/A':
            try:
                current_retracement = float(monthly['从最高点回撤'].replace('%', ''))
                time_range_name = monthly['时间范围']

                if current_retracement > 40:
                    print(f"⚠️  {time_range_name}深度回调: 较近期高点回撤 {monthly['从最高点回撤']}")
                elif current_retracement > 25:
                    print(f"⚠️  {time_range_name}较大回调: 较近期高点回撤 {monthly['从最高点回撤']}")
                elif current_retracement > 15:
                    print(f"📊  {time_range_name}正常回调: 较近期高点回撤 {monthly['从最高点回撤']}")
                elif current_retracement > 8:
                    print(f"📈  {time_range_name}接近高点: 较近期高点回撤 {monthly['从最高点回撤']}")
                elif current_retracement > 0:
                    print(f"🚀  {time_range_name}处于高位: 较近期高点回撤 {monthly['从最高点回撤']}")
                else:
                    print(f"💹  {time_range_name}创新高: 无回撤")
                break
            except ValueError:
                continue

    # 3. 比较不同时间段的回撤
    if len(valid_results) >= 3:
        # 比较短期、中期、长期回撤
        short_term = next((r for r in ordered_results if r['时间范围'] == '最近一个月'), None)
        mid_term = next((r for r in ordered_results if r['时间范围'] == '最近六个月'), None)
        long_term = next((r for r in ordered_results if r['时间范围'] == '最近一年'), None)

        def get_retracement_value(result):
            if result and result['最高到最低回撤'] and result['最高到最低回撤'] != 'N/A':
                try:
                    return float(result['最高到最低回撤'].replace('%', ''))
                except:
                    return None
            return None

        st_val = get_retracement_value(short_term)
        mt_val = get_retracement_value(mid_term)
        lt_val = get_retracement_value(long_term)

        if st_val is not None and mt_val is not None and lt_val is not None:
            if st_val < mt_val < lt_val:
                print(f"📊 回撤特征: 短期({st_val:.1f}%) < 中期({mt_val:.1f}%) < 长期({lt_val:.1f}%) - 回撤逐渐扩大")
            elif st_val > mt_val > lt_val:
                print(f"📊 回撤特征: 短期({st_val:.1f}%) > 中期({mt_val:.1f}%) > 长期({lt_val:.1f}%) - 回撤逐渐收窄")
            else:
                print(f"📊 回撤特征: 短期{st_val:.1f}% / 中期{mt_val:.1f}% / 长期{lt_val:.1f}% - 震荡整理")


def job1():
    """主作业函数"""
    print(f"\n🕒 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    try:
        # 获取交易所信息
        response = requests.get(API_URL, timeout=10)

        if response.status_code != 200:
            print(f"❌ 获取交易所信息失败: {response.status_code}")
            return

        data = response.json()
        print(f"✅ 交易所信息获取成功")
        print(f"📊 交易对总数: {len(data.get('symbols', []))}")

        # 获取所有交易对
        symbols = [symbol['symbol'] for symbol in data.get('symbols', [])]

        # 只分析前5个交易对（测试用）
        # symbols_to_analyze = symbols[:5]  # 测试时用前5个
        symbols_to_analyze = symbols  # 分析所有交易对（慎用，会请求很多次）

        for i, symbol_info in enumerate(symbols_to_analyze, 1):
            print(f"\n{'=' * 60}")
            print(f"📈 正在分析第{i}个交易对: {symbol_info}")
            print('=' * 60)

            try:
                # 获取日K线数据
                print(f"📅 获取{symbol_info}的日K线数据...")
                df_daily = get_kline_data(symbol_info, "1d", 1500)

                if df_daily is not None and len(df_daily) > 0:
                    # 分析回撤
                    results = analyze_retracement(df_daily, symbol_info)

                    if results:
                        # 打印分析报告
                        print_analysis_report(symbol_info, results, df_daily)
                    else:
                        print(f"⚠️  {symbol_info}: 回撤分析失败")
                else:
                    print(f"⚠️  {symbol_info}: 无有效日K线数据")

                # 获取4小时K线数据
                print(f"\n⏰ 获取{symbol_info}的4小时K线数据...")
                df_4h = get_kline_data(symbol_info, "4h", 500)

                if df_4h is not None and len(df_4h) > 0:
                    print(f"✅  获取到 {len(df_4h)} 条4小时K线数据")
                    # 这里可以添加4小时级别的分析
                else:
                    print(f"⚠️  {symbol_info}: 无有效4小时K线数据")

            except Exception as e:
                print(f"❌ 分析{symbol_info}时出错: {e}")
                continue

            print(f"\n✅ {symbol_info} 分析完成")
            print("=" * 60)

    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求失败: {e}")
    except Exception as e:
        print(f"❌ 作业执行失败: {e}")


def main():
    """主函数"""
    print("🚀 开始分析交易对回撤数据")
    print("=" * 60)

    # 立即执行一次
    job1()

    # 如果需要定时执行，取消下面的注释
    """
    scheduler = BlockingScheduler()

    # 每30秒执行一次（生产环境建议更长时间间隔）
    scheduler.add_job(
        job1, 
        'interval', 
        seconds=30,
        max_instances=1,  # 防止并发执行
        misfire_grace_time=30
    )

    print("⏰ 调度器已启动，每30秒执行一次")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n🛑 正在停止调度器...")
        scheduler.shutdown()
        print("✅ 调度器已停止")
    """


if __name__ == "__main__":
    main()