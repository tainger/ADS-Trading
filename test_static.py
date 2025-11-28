from flask import Flask, send_from_directory
import os

# 使用Flask的默认静态文件配置
app = Flask(__name__, 
            static_folder='/Users/rocky/work/python/ADS-Trading/web-ui/build/static',
            static_url_path='/static')

# 主页路由
@app.route('/')
def home():
    return send_from_directory('/Users/rocky/work/python/ADS-Trading/web-ui/build', 'index.html')

# 测试路由 - 直接返回文件内容
@app.route('/test-file')
def test_file():
    file_path = '/Users/rocky/work/python/ADS-Trading/web-ui/build/static/js/main.7ac81178.js'
    with open(file_path, 'r') as f:
        content = f.read()
    return content[:100] + '... (truncated)'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=False)