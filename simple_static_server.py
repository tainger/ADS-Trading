from flask import Flask, send_from_directory
import os

# 获取build目录的绝对路径
build_dir = os.path.abspath('/Users/rocky/work/python/ADS-Trading/web-ui/build')
static_dir = os.path.join(build_dir, 'static')

print(f"Build directory: {build_dir}")
print(f"Static directory: {static_dir}")
print(f"Static files exist: {os.path.exists(static_dir)}")

# 创建Flask应用
app = Flask(__name__)

# 配置静态文件路由
@app.route('/static/<path:path>')
def serve_static(path):
    print(f"Request path: /static/{path}")
    print(f"Static directory: {static_dir}")
    print(f"Full file path: {os.path.join(static_dir, path)}")
    print(f"File exists: {os.path.exists(os.path.join(static_dir, path))}")
    try:
        return send_from_directory(static_dir, path)
    except Exception as e:
        print(f"Error serving file: {e}")
        raise

# 配置主页
@app.route('/')
def home():
    return send_from_directory(build_dir, 'index.html')

if __name__ == '__main__':
    # 使用不同的端口避免冲突
    app.run(host='0.0.0.0', port=8080, debug=False)