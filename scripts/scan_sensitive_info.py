#!/usr/bin/env python3
"""
敏感信息扫描脚本
扫描项目中的敏感信息，为开源发布做准备
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple

class SensitiveInfoScanner:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.results = {
            'secret_keys': [],
            'hardcoded_paths': [],
            'personal_info': [],
            'timestamps': [],
            'chinese_content': [],
            'potential_secrets': []
        }
        
        # 敏感信息模式
        self.patterns = {
            'secret_key': [
                r'SECRET_KEY\s*=\s*[\'"][^\'"]+[\'"]',
                r'secret[_-]?key\s*[:=]\s*[\'"][^\'"]+[\'"]',
                r'password\s*[:=]\s*[\'"][^\'"]+[\'"]',
                r'api[_-]?key\s*[:=]\s*[\'"][^\'"]+[\'"]'
            ],
            'hardcoded_path': [
                r'[\'"][C-Z]:\\[^\'"]*[\'"]',  # Windows路径
                r'[\'"]\/[a-zA-Z][^\'"]*[\'"]',  # Unix路径
                r'os\.path\.join\([^\)]*[\'"][C-Z]:\\[^\'"]*[\'"][^\)]*\)'
            ],
            'personal_info': [
                r'作者[：:]\s*[^\n\r]+',
                r'author[：:]\s*[^\n\r]+',
                r'email[：:]\s*[^\n\r]+',
                r'联系[：:]\s*[^\n\r]+'
            ],
            'timestamp': [
                r'时间[：:]\s*\d{4}[-/]\d{1,2}[-/]\d{1,2}',
                r'更新[：:]\s*\d{4}[-/]\d{1,2}[-/]\d{1,2}',
                r'date[：:]\s*\d{4}[-/]\d{1,2}[-/]\d{1,2}'
            ],
            'chinese_text': [
                r'[\u4e00-\u9fff]+',  # 中文字符
            ]
        }
        
        # 要扫描的文件类型
        self.file_extensions = {'.py', '.js', '.html', '.css', '.md', '.txt', '.json', '.yaml', '.yml'}
        
        # 要忽略的目录
        self.ignore_dirs = {'__pycache__', '.git', 'node_modules', 'dist', 'build', '.vscode'}

    def scan_file(self, file_path: Path) -> Dict:
        """扫描单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            return {'error': str(e)}
        
        file_results = {}
        
        for category, patterns in self.patterns.items():
            matches = []
            for pattern in patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
                    line_num = content[:match.start()].count('\n') + 1
                    matches.append({
                        'line': line_num,
                        'text': match.group().strip(),
                        'context': self._get_context(content, match.start(), match.end())
                    })
            
            if matches:
                file_results[category] = matches
        
        return file_results

    def _get_context(self, content: str, start: int, end: int, context_lines: int = 2) -> str:
        """获取匹配内容的上下文"""
        lines = content.split('\n')
        match_line = content[:start].count('\n')
        
        start_line = max(0, match_line - context_lines)
        end_line = min(len(lines), match_line + context_lines + 1)
        
        context_lines_list = []
        for i in range(start_line, end_line):
            prefix = '>>> ' if i == match_line else '    '
            context_lines_list.append(f"{prefix}{i+1:4d}: {lines[i]}")
        
        return '\n'.join(context_lines_list)

    def scan_project(self) -> Dict:
        """扫描整个项目"""
        print(f"开始扫描项目: {self.project_root}")
        
        for root, dirs, files in os.walk(self.project_root):
            # 过滤忽略的目录
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            
            for file in files:
                file_path = Path(root) / file
                
                # 只扫描指定类型的文件
                if file_path.suffix.lower() not in self.file_extensions:
                    continue
                
                print(f"扫描文件: {file_path.relative_to(self.project_root)}")
                
                file_results = self.scan_file(file_path)
                if file_results and 'error' not in file_results:
                    # 将结果按类别归类
                    for category, matches in file_results.items():
                        if category not in self.results:
                            self.results[category] = []
                        
                        for match in matches:
                            self.results[category].append({
                                'file': str(file_path.relative_to(self.project_root)),
                                'line': match['line'],
                                'text': match['text'],
                                'context': match['context']
                            })
        
        return self.results

    def generate_report(self, output_file: str = None) -> str:
        """生成扫描报告"""
        report = []
        report.append("# 敏感信息扫描报告\n")
        report.append(f"项目路径: {self.project_root}\n")
        report.append("=" * 80 + "\n")
        
        for category, items in self.results.items():
            if not items:
                continue
                
            category_names = {
                'secret_keys': '密钥和密码',
                'hardcoded_paths': '硬编码路径',
                'personal_info': '个人信息',
                'timestamps': '时间戳',
                'chinese_content': '中文内容',
                'potential_secrets': '潜在敏感信息'
            }
            
            report.append(f"\n## {category_names.get(category, category)} ({len(items)} 项)\n")
            
            for i, item in enumerate(items, 1):
                report.append(f"### {i}. {item['file']}:{item['line']}\n")
                report.append(f"**匹配内容**: `{item['text']}`\n")
                report.append("**上下文**:\n```")
                report.append(item['context'])
                report.append("```\n")
        
        report_text = '\n'.join(report)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"报告已保存到: {output_file}")
        
        return report_text

def main():
    """主函数"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scanner = SensitiveInfoScanner(project_root)
    
    # 扫描项目
    results = scanner.scan_project()
    
    # 生成报告
    report_file = os.path.join(project_root, 'sensitive_info_report.md')
    scanner.generate_report(report_file)
    
    # 输出统计信息
    print("\n" + "=" * 50)
    print("扫描完成！统计信息:")
    for category, items in results.items():
        if items:
            print(f"  {category}: {len(items)} 项")
    
    print(f"\n详细报告: {report_file}")

if __name__ == '__main__':
    main()
