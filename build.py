#!/usr/bin/env python3
"""
构建脚本 - 修复版本
"""
import shutil
import subprocess
import sys
from pathlib import Path


def build_react_app():
    """构建 React 应用并复制到后端模板目录"""

    # 路径配置 - 修复路径
    project_root = Path(__file__).parent
    frontend_dir = project_root / 'web-ui'
    backend_templates_dir = project_root / 'ads_trading' / 'web_ui' / 'templates'

    print("🔨 Building ADS Trading Web UI...")
    print(f"📁 前端目录: {frontend_dir}")
    print(f"📁 目标目录: {backend_templates_dir}")

    # 检查前端目录是否存在
    if not frontend_dir.exists():
        print(f"❌ Frontend directory not found: {frontend_dir}")
        print("请先运行: npx create-react-app web-ui")
        return False

    # 检查 package.json 是否存在
    package_json = frontend_dir / 'package.json'
    if not package_json.exists():
        print(f"❌ package.json not found: {package_json}")
        print("这不是一个有效的 React 项目")
        return False

    # 运行 npm build
    try:
        print("📦 Installing npm dependencies...")
        install_result = subprocess.run(
            ['npm', 'install'],
            cwd=frontend_dir,
            capture_output=True,
            text=True
        )

        if install_result.returncode != 0:
            print(f"❌ npm install failed:")
            print(f"STDERR: {install_result.stderr}")
            print(f"STDOUT: {install_result.stdout}")
            return False

        print("✅ npm install completed")

        print("🏗️ Building React app...")
        build_result = subprocess.run(
            ['npm', 'run', 'build'],
            cwd=frontend_dir,
            capture_output=True,
            text=True
        )

        if build_result.returncode != 0:
            print(f"❌ npm build failed:")
            print(f"STDERR: {build_result.stderr}")
            print(f"STDOUT: {build_result.stdout}")
            return False

        print("✅ React build completed")

        # 复制构建文件
        build_output_dir = frontend_dir / 'build'
        if build_output_dir.exists():
            print(f"📁 Build output found: {build_output_dir}")

            # 确保目标目录存在
            backend_templates_dir.mkdir(parents=True, exist_ok=True)

            # 清空目标目录
            if backend_templates_dir.exists():
                print("🧹 Cleaning target directory...")
                shutil.rmtree(backend_templates_dir)

            # 复制新构建的文件
            print("📤 Copying build files...")
            shutil.copytree(build_output_dir, backend_templates_dir)
            print(f"✅ React app built and copied to {backend_templates_dir}")

            # 显示构建信息
            files = list(backend_templates_dir.rglob('*'))
            files_count = len([f for f in files if f.is_file()])
            print(f"📁 Build files: {files_count} files")

            # 显示关键文件
            key_files = ['index.html', 'static/js', 'static/css']
            for file in key_files:
                file_path = backend_templates_dir / file
                if file_path.exists():
                    print(f"   ✅ {file}")
                else:
                    print(f"   ❌ {file} (missing)")

            return True
        else:
            print("❌ Build output directory not found")
            print("请检查 React 项目配置")
            return False

    except Exception as e:
        print(f"❌ Build error: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_fallback_html():
    """创建备用 HTML 文件"""
    print("🔄 Creating fallback HTML...")

    backend_templates_dir = Path(__file__).parent / 'ads-trading' / 'web_ui' / 'templates'
    backend_templates_dir.mkdir(parents=True, exist_ok=True)

    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>ADS Trading</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial; background: #0f1419; color: white; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #1e3c72, #2a5298); padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 20px; }
        .card { background: #1a202c; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #2d3748; }
        .market-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px; }
        .market-item { background: #2d3748; padding: 15px; border-radius: 6px; border-left: 4px solid #4299e1; }
        .positive { color: #48bb78; font-weight: bold; }
        .negative { color: #f56565; font-weight: bold; }
        button { padding: 10px 20px; margin: 5px; border: none; border-radius: 4px; cursor: pointer; }
        .buy-btn { background: #48bb78; color: white; }
        .sell-btn { background: #f56565; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 ADS Trading System</h1>
            <p>备用界面 - React 构建失败</p>
        </div>

        <div class="card">
            <h2>系统状态</h2>
            <p>后端 API 服务正常运行中</p>
            <button onclick="testAPI()">测试 API 连接</button>
            <div id="apiResult"></div>
        </div>

        <div class="card">
            <h2>交易面板</h2>
            <button class="buy-btn" onclick="simulateTrade('buy')">买入</button>
            <button class="sell-btn" onclick="simulateTrade('sell')">卖出</button>
        </div>
    </div>

    <script>
        async function testAPI() {
            try {
                const response = await fetch('/api/market');
                const data = await response.json();
                document.getElementById('apiResult').innerHTML = 
                    '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            } catch (error) {
                document.getElementById('apiResult').innerHTML = 
                    '<p style="color: red;">错误: ' + error.message + '</p>';
            }
        }

        function simulateTrade(side) {
            alert((side === 'buy' ? '买入' : '卖出') + '操作模拟执行');
        }

        // 自动测试 API
        testAPI();
    </script>
</body>
</html>"""

    with open(backend_templates_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ Fallback HTML created at: {backend_templates_dir / 'index.html'}")


if __name__ == '__main__':
    print("🚀 Starting build process...")
    success = build_react_app()

    if not success:
        print("\n🔄 Build failed, creating fallback HTML...")
        create_fallback_html()

    sys.exit(0 if success else 1)