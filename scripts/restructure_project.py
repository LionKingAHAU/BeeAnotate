#!/usr/bin/env python3
"""
项目结构重构脚本
将现有项目重构为标准的开源项目结构
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List

class ProjectRestructurer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.new_structure = {
            'src': {
                'app': {},
                'static': {
                    'css': {},
                    'js': {},
                    'fonts': {},
                    'vendor': {}
                },
                'templates': {},
                'locales': {
                    'en': {
                        'LC_MESSAGES': {}
                    },
                    'zh': {
                        'LC_MESSAGES': {}
                    }
                }
            },
            'data': {
                'annotations': {},
                'exports': {},
                'uploads': {},
                'processed_masks': {}
            },
            'tests': {},
            'docs': {},
            'scripts': {},
            'config': {}
        }
        
        self.file_mappings = {
            # 源代码文件
            'run.py': 'src/main.py',
            'app/__init__.py': 'src/app/__init__.py',
            'app/config.py': 'src/app/config.py',
            'app/models.py': 'src/app/models.py',
            'app/routes.py': 'src/app/routes.py',
            
            # 静态资源
            'static/css/': 'src/static/css/',
            'static/js/': 'src/static/js/',
            'static/fonts/': 'src/static/fonts/',
            
            # 模板文件
            'templates/': 'src/templates/',
            
            # 数据文件（合并重复目录）
            'data/annotations/': 'data/annotations/',
            'data/exports/': 'data/exports/',
            'data/processed_masks/': 'data/processed_masks/',
            'static/uploads/': 'data/uploads/',
            
            # 配置文件
            'config/': 'config/',
            
            # 脚本文件
            'scripts/': 'scripts/',
            
            # 项目文件
            'requirements.txt': 'requirements.txt',
            '.env.template': '.env.template',
            '.gitignore': '.gitignore'
        }
        
        # 要删除的文件和目录
        self.files_to_remove = [
            'bee_annotation_tool.spec',
            'bee_annotation_tool_windows.spec',
            'start_windows.bat',
            'Windows打包说明.md',
            'Windows部署说明.md',
            '透明度调整说明.md',
            'build/',
            'dist/',
            'bee_annotation_data/',
            'backup_before_cleanup/',
            'sensitive_info_report.md',
            'cleanup_report.md'
        ]
    
    def create_new_structure(self):
        """创建新的目录结构"""
        print("创建新的目录结构...")
        
        def create_dirs(structure: Dict, base_path: Path):
            for name, content in structure.items():
                dir_path = base_path / name
                dir_path.mkdir(exist_ok=True)
                print(f"  创建目录: {dir_path.relative_to(self.project_root)}")

                if isinstance(content, dict):
                    create_dirs(content, dir_path)
        
        # 创建新结构目录
        new_root = self.project_root / 'new_structure'
        if new_root.exists():
            shutil.rmtree(new_root)
        new_root.mkdir()
        
        create_dirs(self.new_structure, new_root)
        return new_root
    
    def copy_files(self, new_root: Path):
        """复制文件到新结构"""
        print("复制文件到新结构...")
        
        for old_path, new_path in self.file_mappings.items():
            src = self.project_root / old_path
            dst = new_root / new_path
            
            if src.exists():
                if src.is_dir():
                    if dst.exists():
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                    print(f"  复制目录: {old_path} -> {new_path}")
                else:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                    print(f"  复制文件: {old_path} -> {new_path}")
            else:
                print(f"  警告: 源文件不存在 {old_path}")
    
    def update_imports_and_paths(self, new_root: Path):
        """更新导入语句和路径引用"""
        print("更新导入语句和路径引用...")
        
        # 更新 main.py 中的导入
        main_py = new_root / 'src' / 'main.py'
        if main_py.exists():
            content = main_py.read_text(encoding='utf-8')
            content = content.replace('from app import create_app', 'from app import create_app')
            main_py.write_text(content, encoding='utf-8')
            print("  ✓ 更新 main.py")
        
        # 更新 config.py 中的路径
        config_py = new_root / 'src' / 'app' / 'config.py'
        if config_py.exists():
            content = config_py.read_text(encoding='utf-8')
            
            # 更新路径计算
            old_base_dir = "os.path.dirname(os.path.dirname(os.path.abspath(__file__)))"
            new_base_dir = "os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))"
            content = content.replace(old_base_dir, new_base_dir)
            
            # 更新目录路径
            content = content.replace(
                "os.path.join(BASE_DIR, 'bee_annotation_data', 'static')",
                "os.path.join(BASE_DIR, 'src', 'static')"
            )
            content = content.replace(
                "os.path.join(BASE_DIR, 'bee_annotation_data', 'data')",
                "os.path.join(BASE_DIR, 'data')"
            )
            
            config_py.write_text(content, encoding='utf-8')
            print("  ✓ 更新 config.py")
    
    def create_project_files(self, new_root: Path):
        """创建标准的项目文件"""
        print("创建标准项目文件...")
        
        # 创建 README.md
        readme_content = """# Bee Cell Annotation Tool

A web-based tool for annotating bee cell types in honeycomb images.

## Features

- Interactive web interface for image annotation
- Support for 8 different bee cell types
- Zoom and pan functionality
- Export annotations in multiple formats
- Internationalization support (English/Chinese)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd bee_cell_annotation
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.template .env
# Edit .env with your settings
```

4. Run the application:
```bash
python src/main.py
```

## Usage

1. Open your browser and navigate to `http://localhost:5000`
2. Upload honeycomb images
3. Start annotating cell types
4. Export your annotations

## Cell Types

- **Eggs**: White oval-shaped, ≤3mm length
- **Larvae**: White worm-like, >3mm length
- **Capped Brood**: Light yellow wax cap
- **Pollen**: Colorful granular particles
- **Nectar**: Transparent liquid in open cells
- **Honey**: Thick wax-sealed cells
- **Other**: Empty cells or uncertain types
- **Honeycomb**: Hexagonal cell structure

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
"""
        
        (new_root / 'README.md').write_text(readme_content, encoding='utf-8')
        print("  ✓ 创建 README.md")
        
        # 创建 LICENSE
        license_content = """MIT License

Copyright (c) 2025 Bee Cell Annotation Tool Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
        
        (new_root / 'LICENSE').write_text(license_content, encoding='utf-8')
        print("  ✓ 创建 LICENSE")
        
        # 创建 CONTRIBUTING.md
        contributing_content = """# Contributing to Bee Cell Annotation Tool

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Development Setup

1. Fork the repository
2. Clone your fork
3. Install dependencies: `pip install -r requirements.txt`
4. Create a feature branch: `git checkout -b feature-name`

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Write tests for new features

## Submitting Changes

1. Make your changes
2. Add tests if applicable
3. Update documentation
4. Submit a pull request

## Reporting Issues

Please use the GitHub issue tracker to report bugs or request features.
"""
        
        (new_root / 'CONTRIBUTING.md').write_text(contributing_content, encoding='utf-8')
        print("  ✓ 创建 CONTRIBUTING.md")
    
    def generate_restructure_report(self, new_root: Path):
        """生成重构报告"""
        report_content = f"""# 项目结构重构报告

## 新的目录结构

```
bee_cell_annotation/
├── src/                          # 源代码
│   ├── app/                      # Flask应用
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── models.py
│   │   └── routes.py
│   ├── static/                   # 静态资源
│   │   ├── css/
│   │   ├── js/
│   │   └── fonts/
│   ├── templates/                # HTML模板
│   ├── locales/                  # 国际化资源
│   │   ├── en/
│   │   └── zh/
│   └── main.py                   # 主入口文件
├── data/                         # 数据目录
│   ├── annotations/              # 标注数据
│   ├── exports/                  # 导出数据
│   ├── uploads/                  # 上传图像
│   └── processed_masks/          # 处理过的掩码
├── tests/                        # 测试代码
├── docs/                         # 文档
├── scripts/                      # 构建和工具脚本
├── config/                       # 配置文件
├── requirements.txt              # 依赖列表
├── .env.template                 # 环境变量模板
├── .gitignore                    # Git忽略文件
├── README.md                     # 项目说明
├── LICENSE                       # 许可证
└── CONTRIBUTING.md               # 贡献指南
```

## 主要改进

1. **简化路径深度**: 从3层深度减少到2层
2. **标准化结构**: 符合开源项目最佳实践
3. **清晰分离**: 源码、数据、配置分离
4. **国际化准备**: 预留语言资源目录
5. **完整文档**: 添加标准开源文档

## 文件映射

"""
        
        for old_path, new_path in self.file_mappings.items():
            report_content += f"- `{old_path}` -> `{new_path}`\n"
        
        report_content += f"""
## 删除的文件

"""
        
        for file_path in self.files_to_remove:
            report_content += f"- `{file_path}`\n"
        
        report_content += f"""
## 下一步

1. 检查新结构: `{new_root.relative_to(self.project_root)}/`
2. 测试应用程序功能
3. 如果确认无问题，替换原项目结构
4. 继续国际化实现

新结构已创建在: {new_root}
"""
        
        report_file = self.project_root / 'restructure_report.md'
        report_file.write_text(report_content, encoding='utf-8')
        print(f"重构报告已保存到: {report_file}")
    
    def run_restructure(self):
        """执行完整的重构流程"""
        print("开始项目结构重构...")
        print("=" * 60)
        
        # 创建新结构
        new_root = self.create_new_structure()
        
        # 复制文件
        self.copy_files(new_root)
        
        # 更新引用
        self.update_imports_and_paths(new_root)
        
        # 创建项目文件
        self.create_project_files(new_root)
        
        # 生成报告
        self.generate_restructure_report(new_root)
        
        print("=" * 60)
        print("项目结构重构完成！")
        print(f"新结构位置: {new_root}")

def main():
    """主函数"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    restructurer = ProjectRestructurer(project_root)
    restructurer.run_restructure()

if __name__ == '__main__':
    main()
