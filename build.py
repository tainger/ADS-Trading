#!/usr/bin/env python3
"""
构建脚本 - 将 React 前端构建文件复制到 Python 包中
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path


def build_react_app():
    """构建 React 应用并复制到后端模板目录"""

    # 路径配置
    project_root = Path(__file__).parent
    frontend_dir = project_root / 'web-ui'
    backend_templates_dir = project_root / 'ads-trading' / 'web_ui' / 'templates'

    print("🔨 Building ADS Trading Web UI...")

    # 检查前端目录是否存在
    if not frontend_dir.exists():
        print(f"❌ Frontend directory not found: {frontend_dir}")
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
            print(f"❌ npm install failed: {install_result.stderr}")
            return False

        print("🏗️ Building React app...")
        build_result = subprocess.run(
            ['npm', 'run', 'build'],
            cwd=frontend_dir,
            capture_output=True,
            text=True
        )

        if build_result.returncode != 0:
            print(f"❌ npm build failed: {build_result.stderr}")
            return False

        # 复制构建文件
        build_output_dir = frontend_dir / 'build'
        if build_output_dir.exists():
            # 确保目标目录存在
            backend_templates_dir.mkdir(parents=True, exist_ok=True)

            # 清空目标目录
            if backend_templates_dir.exists():
                shutil.rmtree(backend_templates_dir)

            # 复制新构建的文件
            shutil.copytree(build_output_dir, backend_templates_dir)
            print(f"✅ React app built and copied to {backend_templates_dir}")

            # 显示构建信息
            files_count = len(list(backend_templates_dir.rglob('*')))
            print(f"📁 Build files: {files_count} files")
            return True
        else:
            print("❌ Build output directory not found")
            return False

    except Exception as e:
        print(f"❌ Build error: {e}")
        return False


if __name__ == '__main__':
    success = build_react_app()
    sys.exit(0 if success else 1)