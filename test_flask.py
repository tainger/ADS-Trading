from flask import Flask, send_file
import os

# 禁用默认静态文件路由
app = Flask(__name__, static_folder=None)

# 设置静态文件目录
static_dir = '/Users/rocky/work/python/ADS-Trading/ads_trading/web_ui/templates/static'

@app.route('/')
def index():
    return "Hello, Flask!"

# 直接使用send_file来提供静态文件
@app.route('/static/<path:filename>')
def serve_static(filename):
    import os
    from flask import send_file
    print(f"DEBUG - Requested filename: {filename}")
    print(f"DEBUG - Static directory: {static_dir}")
    file_path = os.path.join(static_dir, filename)
    print(f"DEBUG - Full file path: {file_path}")
    print(f"DEBUG - File exists: {os.path.exists(file_path)}")
    
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        return f"File not found: {file_path}", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)