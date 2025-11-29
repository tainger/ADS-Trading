#!/usr/bin/env python
"""
启动Web UI服务器的脚本
"""

from ads_trading.web_ui.server import WebServer

if __name__ == "__main__":
    # 创建Web服务器实例
    web_server = WebServer()
    
    # 启动服务器
    web_server.run(host='0.0.0.0', port=5000, debug=False)
