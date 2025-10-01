#!/usr/bin/env python3
"""
蜂格标注工具配置文件
"""

import os
import secrets
import sys

def get_resource_path(relative_path):
    """获取资源文件的绝对路径，适配PyInstaller打包"""
    try:
        # PyInstaller创建临时文件夹，并将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        # 开发环境中使用当前目录
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_app_data_dir():
    """获取应用数据目录，适配打包环境"""
    if getattr(sys, 'frozen', False):
        # 打包环境：在可执行文件同目录创建数据文件夹
        app_dir = os.path.dirname(sys.executable)
    else:
        # 开发环境：使用项目根目录
        app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    return app_dir

def init_data_from_package():
    """从打包的资源中初始化数据到工作目录"""
    import shutil

    if not getattr(sys, 'frozen', False):
        return  # 开发环境不需要初始化

    # 获取打包的数据路径和目标路径
    packaged_data_dir = get_resource_path('data')
    packaged_static_dir = get_resource_path('static')

    target_data_dir = os.path.join(BASE_DIR, 'data')
    target_static_dir = os.path.join(BASE_DIR, 'src', 'static')

    # 快速初始化：只初始化必要的数据文件
    if os.path.exists(packaged_data_dir) and (not os.path.exists(target_data_dir) or not os.listdir(target_data_dir)):
        print("🔄 正在初始化数据文件...")
        os.makedirs(target_data_dir, exist_ok=True)
        try:
            if os.path.exists(os.path.join(packaged_data_dir, 'annotations')):
                shutil.copytree(os.path.join(packaged_data_dir, 'annotations'),
                              os.path.join(target_data_dir, 'annotations'),
                              dirs_exist_ok=True)
            if os.path.exists(os.path.join(packaged_data_dir, 'processed_masks')):
                shutil.copytree(os.path.join(packaged_data_dir, 'processed_masks'),
                              os.path.join(target_data_dir, 'processed_masks'),
                              dirs_exist_ok=True)
            if os.path.exists(os.path.join(packaged_data_dir, 'exports')):
                shutil.copytree(os.path.join(packaged_data_dir, 'exports'),
                              os.path.join(target_data_dir, 'exports'),
                              dirs_exist_ok=True)
            print("✅ 数据文件初始化完成")
        except Exception as e:
            print(f"⚠️  数据文件初始化出现问题: {e}")

    # 初始化静态文件（包括上传的图像）
    if os.path.exists(packaged_static_dir) and (not os.path.exists(target_static_dir) or not os.listdir(target_static_dir)):
        print("🔄 正在初始化静态资源...")
        os.makedirs(target_static_dir, exist_ok=True)

        # 先复制CSS和JS文件（小文件，快速）
        for subdir in ['css', 'js', 'fonts']:
            src_dir = os.path.join(packaged_static_dir, subdir)
            if os.path.exists(src_dir):
                shutil.copytree(src_dir, os.path.join(target_static_dir, subdir), dirs_exist_ok=True)

        # 创建uploads目录但暂不复制大文件（按需加载）
        uploads_dst = os.path.join(target_static_dir, 'uploads')
        os.makedirs(uploads_dst, exist_ok=True)

        # 创建一个标记文件，表示需要后台初始化
        uploads_src = os.path.join(packaged_static_dir, 'uploads')
        if os.path.exists(uploads_src) and not os.path.exists(os.path.join(uploads_dst, '.initialized')):
            with open(os.path.join(uploads_dst, '.need_init'), 'w') as f:
                f.write(uploads_src)
            print("📝 图像文件将在后台初始化，应用可立即使用")

        print("✅ 静态资源初始化完成")

def init_uploads_background():
    """后台初始化uploads目录"""
    import threading
    import shutil

    def background_copy():
        target_static_dir = os.path.join(BASE_DIR, 'src', 'static')
        uploads_dst = os.path.join(target_static_dir, 'uploads')
        need_init_file = os.path.join(uploads_dst, '.need_init')

        if os.path.exists(need_init_file):
            try:
                with open(need_init_file, 'r') as f:
                    uploads_src = f.read().strip()

                if os.path.exists(uploads_src):
                    print("🔄 开始后台复制图像文件...")

                    # 复制所有图像文件
                    for filename in os.listdir(uploads_src):
                        src_file = os.path.join(uploads_src, filename)
                        dst_file = os.path.join(uploads_dst, filename)
                        if os.path.isfile(src_file) and not os.path.exists(dst_file):
                            shutil.copy2(src_file, dst_file)

                    # 创建完成标记
                    with open(os.path.join(uploads_dst, '.initialized'), 'w') as f:
                        f.write('completed')

                    # 删除需要初始化的标记
                    os.remove(need_init_file)
                    print("✅ 后台图像文件复制完成")

            except Exception as e:
                print(f"⚠️  后台复制出现问题: {e}")

    # 启动后台线程
    if getattr(sys, 'frozen', False):  # 只在打包环境中启用
        thread = threading.Thread(target=background_copy, daemon=True)
        thread.start()

# 基础路径
BASE_DIR = get_app_data_dir()
PROJECT_ROOT = BASE_DIR

# 目录配置 - 在可执行文件同目录创建数据文件夹
STATIC_DIR = os.path.join(BASE_DIR, 'src', 'static')
UPLOAD_DIR = os.path.join(STATIC_DIR, 'uploads')
DATA_DIR = os.path.join(BASE_DIR, 'data')
ANNOTATIONS_DIR = os.path.join(DATA_DIR, 'annotations')
EXPORTS_DIR = os.path.join(DATA_DIR, 'exports')

# 源图像目录（原始的imgs文件夹）
SOURCE_IMGS_DIR = os.path.join(PROJECT_ROOT, 'imgs')

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tif', 'tiff'}

# 8类蜂格定义（新增蜂巢类别）
CELL_CLASSES = {
    'eggs': {
        'name_key': 'cell_class.eggs.name',
        'color': '#FFE6E6',
        'border': '#FF4444',
        'description_key': 'cell_class.eggs.description'
    },
    'larvae': {
        'name_key': 'cell_class.larvae.name',
        'color': '#E6F3FF',
        'border': '#4488FF',
        'description_key': 'cell_class.larvae.description'
    },
    'capped_brood': {
        'name_key': 'cell_class.capped_brood.name',
        'color': '#FFF4E6',
        'border': '#FFB344',
        'description_key': 'cell_class.capped_brood.description'
    },
    'pollen': {
        'name_key': 'cell_class.pollen.name',
        'color': '#F0E6FF',
        'border': '#AA44FF',
        'description_key': 'cell_class.pollen.description'
    },
    'nectar': {
        'name_key': 'cell_class.nectar.name',
        'color': '#E6FFE6',
        'border': '#44FF44',
        'description_key': 'cell_class.nectar.description'
    },
    'honey': {
        'name_key': 'cell_class.honey.name',
        'color': '#FFFFE6',
        'border': '#FFFF44',
        'description_key': 'cell_class.honey.description'
    },
    'other': {
        'name_key': 'cell_class.other.name',
        'color': '#F0F0F0',
        'border': '#888888',
        'description_key': 'cell_class.other.description'
    },
    'honeycomb': {
        'name_key': 'cell_class.honeycomb.name',
        'color': '#F4E4BC',
        'border': '#8B4513',
        'description_key': 'cell_class.honeycomb.description'
    }
}

# Flask配置
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # 确保目录存在
    @staticmethod
    def init_directories():
        """初始化所有必要的目录"""
        # 首先从打包资源初始化数据
        init_data_from_package()

        dirs = [
            STATIC_DIR,
            UPLOAD_DIR,
            DATA_DIR,
            ANNOTATIONS_DIR,
            EXPORTS_DIR,
            os.path.join(STATIC_DIR, 'css'),
            os.path.join(STATIC_DIR, 'js')
        ]

        for directory in dirs:
            os.makedirs(directory, exist_ok=True)