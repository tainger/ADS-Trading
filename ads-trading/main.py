#!/usr/bin/env python3
"""
ADS Trading 主入口文件
"""
import os
import sys
import argparse
from .web_ui.server import WebServer


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='ADS Trading System')
    parser.add_argument('--port', type=int, default=5000, help='Web server port')
    parser.add_argument('--host', default='0.0.0.0', help='Web server host')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')

    args = parser.parse_args()

    # 创建并启动 Web 服务器
    server = WebServer()

    print("🚀 Starting ADS Trading System...")
    print(f"📊 Dashboard: http://{args.host}:{args.port}")
    print("⏹️  Press Ctrl+C to stop")

    try:
        server.run(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        print("\n👋 Shutting down ADS Trading System...")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()