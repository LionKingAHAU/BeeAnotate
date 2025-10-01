#!/usr/bin/env python3
"""

# Load environment variables before importing app
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__))))
from config.env_loader import load_environment
load_environment()


Bee Cell Annotation Tool - Main Entry Point
A web-based tool for annotating bee cell types in honeycomb images
"""

from app import create_app
import os

def find_available_port(start_port=5006, max_attempts=10):
    """查找可用端口"""
    import socket

    for i in range(max_attempts):
        port = start_port + i
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue

    # 如果前面的端口都被占用，尝试系统分配
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('localhost', 0))
        return s.getsockname()[1]

def open_browser(url):
    """自动打开浏览器"""
    import webbrowser
    import threading
    import time

    def delayed_open():
        time.sleep(1.5)  # 等待服务器启动
        try:
            webbrowser.open(url)
            print(f"🌐 已自动打开浏览器: {url}")
        except Exception as e:
            print(f"⚠️  无法自动打开浏览器: {e}")
            print(f"请手动访问: {url}")

    thread = threading.Thread(target=delayed_open)
    thread.daemon = True
    thread.start()

def main():
    """主函数"""
    print("🚀 启动蜂格8类分类标注工具")
    print("=" * 50)

    # 创建Flask应用
    app = create_app()

    # 确保上传文件夹存在并初始化数据
    from app.config import UPLOAD_DIR, Config, init_uploads_background
    import os
    Config.init_directories()  # 这会自动初始化所有数据

    # 启动后台图像文件初始化
    init_uploads_background()

    # 查找可用端口
    import sys
    start_port = 5006 if getattr(sys, 'frozen', False) else 5005
    port = find_available_port(start_port)

    print("✅ 蜂格标注工具准备完成")
    print(f"🌐 访问地址: http://localhost:{port}")
    print("📋 功能: 8类蜂格分类标注（新增蜂巢类别）")

    if port != start_port:
        print(f"⚠️  原端口 {start_port} 被占用，已自动切换到端口 {port}")

    print("=" * 50)

    # 自动打开浏览器（仅在打包环境中）
    if getattr(sys, 'frozen', False):
        open_browser(f"http://localhost:{port}")

    # 启动应用
    try:
        app.run(host='0.0.0.0', port=port, debug=False if getattr(sys, 'frozen', False) else True)
    except KeyboardInterrupt:
        print("\n👋 蜂格标注工具已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        input("按回车键退出...")

if __name__ == '__main__':
    main() 