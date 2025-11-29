#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将CSV格式的K线数据导入到数据库中
"""

import sys
import os

# 将项目根目录添加到Python路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from datetime import datetime
from trader.constant import Exchange, Interval
from trader.object import BarData
from trader.database import get_database

def import_csv_to_database(csv_path: str, symbol: str, exchange: str, interval: str):
    """
    将CSV文件导入到数据库
    
    :param csv_path: CSV文件路径
    :param symbol: 交易对，如BTCUSDT
    :param exchange: 交易所，如binance
    :param interval: K线周期，如1min
    """
    # 读取CSV文件
    df = pd.read_csv(csv_path)
    print(f"成功读取CSV文件，共 {len(df)} 条数据")
    
    # 转换交易所和周期为枚举类型
    exchange_enum = Exchange(exchange.upper())
    interval_enum = Interval(interval)
    
    # 将数据转换为BarData对象列表
    bars = []
    for index, row in df.iterrows():
        # 转换时间格式
        datetime_str = row['Datetime']
        dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        
        # 创建BarData对象
        bar = BarData(
            symbol=symbol,
            exchange=exchange_enum,
            datetime=dt,
            interval=interval_enum,
            volume=float(row['Volume']),
            turnover=0.0,  # CSV中没有提供
            open_interest=0.0,  # CSV中没有提供
            open_price=float(row['Open']),
            high_price=float(row['High']),
            low_price=float(row['Low']),
            close_price=float(row['Close']),
            gateway_name="DB"
        )
        bars.append(bar)
    
    print(f"成功转换为BarData对象，共 {len(bars)} 个")
    
    # 获取数据库实例
    database = get_database()
    
    # 保存数据到数据库
    print("开始保存数据到数据库...")
    success = database.save_bar_data(bars)
    
    if success:
        print("数据导入成功！")
    else:
        print("数据导入失败！")

if __name__ == "__main__":
    # 配置参数
    CSV_PATH = "/Users/rocky/work/python/ADS-Trading/ads_trading/binance/BTCUSDT_vnpy.csv"
    SYMBOL = "BTCUSDT"
    EXCHANGE = "binance"
    INTERVAL = "1m"
    
    # 执行导入
    import_csv_to_database(CSV_PATH, SYMBOL, EXCHANGE, INTERVAL)
