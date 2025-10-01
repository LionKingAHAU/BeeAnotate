#!/usr/bin/env python3
"""
敏感信息清理脚本
自动清理项目中的敏感信息，为开源发布做准备
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime

class SensitiveInfoCleaner:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / 'backup_before_cleanup'
        self.changes_log = []
        
    def create_backup(self):
        """创建备份"""
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        print(f"创建备份到: {self.backup_dir}")
        
        # 备份关键文件
        files_to_backup = [
            'run.py',
            'app/config.py',
            'app/routes.py',
            'requirements.txt'
        ]
        
        for file_path in files_to_backup:
            src = self.project_root / file_path
            if src.exists():
                dst = self.backup_dir / file_path
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                print(f"  备份: {file_path}")
    
    def clean_file_headers(self):
        """清理文件头部的个人信息"""
        print("清理文件头部信息...")
        
        # 清理 run.py
        run_py = self.project_root / 'run.py'
        if run_py.exists():
            content = run_py.read_text(encoding='utf-8')
            
            # 替换文件头部注释
            new_header = '''#!/usr/bin/env python3
"""
Bee Cell Annotation Tool - Main Entry Point
A web-based tool for annotating bee cell types in honeycomb images
"""'''
            
            # 使用正则表达式替换文档字符串
            pattern = r'#!/usr/bin/env python3\s*"""[^"]*"""'
            new_content = re.sub(pattern, new_header, content, flags=re.DOTALL)
            
            if new_content != content:
                run_py.write_text(new_content, encoding='utf-8')
                self.changes_log.append("清理 run.py 文件头部信息")
                print("  ✓ 清理 run.py")
    
    def clean_config_file(self):
        """清理配置文件中的敏感信息"""
        print("清理配置文件...")
        
        config_py = self.project_root / 'app' / 'config.py'
        if config_py.exists():
            content = config_py.read_text(encoding='utf-8')
            
            # 替换硬编码的SECRET_KEY
            pattern = r"SECRET_KEY\s*=\s*['\"][^'\"]+['\"]"
            replacement = "SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)"
            
            new_content = re.sub(pattern, replacement, content)
            
            # 添加必要的导入
            if 'import secrets' not in new_content:
                import_pattern = r'(import os\s*\n)'
                new_content = re.sub(import_pattern, r'\1import secrets\n', new_content)
            
            if new_content != content:
                config_py.write_text(new_content, encoding='utf-8')
                self.changes_log.append("清理 app/config.py 中的硬编码密钥")
                print("  ✓ 清理 app/config.py")
    
    def clean_requirements(self):
        """清理 requirements.txt 中的中文注释"""
        print("清理 requirements.txt...")
        
        req_file = self.project_root / 'requirements.txt'
        if req_file.exists():
            content = req_file.read_text(encoding='utf-8')
            
            # 替换中文注释为英文
            replacements = {
                '# 蜂格标注工具依赖项': '# Bee Cell Annotation Tool Dependencies',
                '# Flask Web框架及相关依赖': '# Flask Web Framework and Related Dependencies',
                '# 用于文件处理和安全文件名': '# For file handling and secure filenames',
                '# 标准库依赖（这些通常已包含在Python中，但为了完整性列出）': '# Standard library dependencies (usually included in Python)',
                '# os, json, csv, shutil, datetime, logging 都是Python标准库': '# os, json, csv, shutil, datetime, logging are Python standard libraries',
                '# 可选：如果需要更好的日志处理': '# Optional: for better logging',
                '# 可选：如果需要图像处理功能': '# Optional: for image processing',
                '# 可选：如果需要更好的开发体验': '# Optional: for better development experience'
            }
            
            new_content = content
            for chinese, english in replacements.items():
                new_content = new_content.replace(chinese, english)
            
            if new_content != content:
                req_file.write_text(new_content, encoding='utf-8')
                self.changes_log.append("清理 requirements.txt 中的中文注释")
                print("  ✓ 清理 requirements.txt")
    
    def create_gitignore(self):
        """创建 .gitignore 文件"""
        print("创建 .gitignore 文件...")
        
        gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# celery beat schedule file
celerybeat-schedule

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project specific
backup_before_cleanup/
sensitive_info_report.md
config/config.py
*.exe
*.zip
bee_annotation_data/
"""
        
        gitignore_file = self.project_root / '.gitignore'
        gitignore_file.write_text(gitignore_content, encoding='utf-8')
        self.changes_log.append("创建 .gitignore 文件")
        print("  ✓ 创建 .gitignore")
    
    def generate_cleanup_report(self):
        """生成清理报告"""
        report_content = f"""# 敏感信息清理报告

清理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 清理内容

"""
        
        for change in self.changes_log:
            report_content += f"- {change}\n"
        
        report_content += f"""
## 备份位置

原始文件已备份到: {self.backup_dir}

## 后续步骤

1. 复制 .env.template 到 .env 并配置环境变量
2. 复制 config/config.template.py 到 config/config.py 并根据需要修改
3. 检查并测试应用程序功能
4. 删除备份文件（如果确认无问题）

## 注意事项

- 请确保在生产环境中设置强密码的 SECRET_KEY
- 检查所有配置是否正确
- 测试应用程序的所有功能
"""
        
        report_file = self.project_root / 'cleanup_report.md'
        report_file.write_text(report_content, encoding='utf-8')
        print(f"清理报告已保存到: {report_file}")
    
    def run_cleanup(self):
        """执行完整的清理流程"""
        print("开始敏感信息清理...")
        print("=" * 50)
        
        # 创建备份
        self.create_backup()
        
        # 执行清理
        self.clean_file_headers()
        self.clean_config_file()
        self.clean_requirements()
        self.create_gitignore()
        
        # 生成报告
        self.generate_cleanup_report()
        
        print("=" * 50)
        print("敏感信息清理完成！")
        print(f"共完成 {len(self.changes_log)} 项清理")

def main():
    """主函数"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cleaner = SensitiveInfoCleaner(project_root)
    cleaner.run_cleanup()

if __name__ == '__main__':
    main()
