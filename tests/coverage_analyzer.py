#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试覆盖率分析工具
"""

import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Any
import importlib.util


class CoverageAnalyzer:
    """测试覆盖率分析器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.source_files = []
        self.test_files = []
        self.coverage_data = {}
        
    def scan_project(self):
        """扫描项目文件"""
        # 扫描源文件
        for py_file in self.project_root.glob("*.py"):
            if not py_file.name.startswith('test_') and py_file.name not in ['setup.py', 'run_tests.py']:
                self.source_files.append(py_file)
        
        for py_file in self.project_root.glob("utils/*.py"):
            if py_file.name != '__init__.py':
                self.source_files.append(py_file)
        
        # 扫描测试文件
        tests_dir = self.project_root / "tests"
        if tests_dir.exists():
            for py_file in tests_dir.glob("test_*.py"):
                self.test_files.append(py_file)
    
    def analyze_source_file(self, file_path: Path) -> Dict[str, Any]:
        """分析源文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            analysis = {
                'file': str(file_path),
                'classes': [],
                'functions': [],
                'methods': [],
                'lines_of_code': len([line for line in content.split('\n') if line.strip() and not line.strip().startswith('#')])
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'line': node.lineno,
                        'methods': []
                    }
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            class_info['methods'].append({
                                'name': item.name,
                                'line': item.lineno,
                                'is_async': isinstance(item, ast.AsyncFunctionDef)
                            })
                    
                    analysis['classes'].append(class_info)
                
                elif isinstance(node, ast.FunctionDef) and not self._is_method(node, tree):
                    analysis['functions'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'is_async': isinstance(node, ast.AsyncFunctionDef)
                    })
            
            return analysis
            
        except Exception as e:
            return {
                'file': str(file_path),
                'error': str(e),
                'classes': [],
                'functions': [],
                'methods': [],
                'lines_of_code': 0
            }
    
    def _is_method(self, func_node: ast.FunctionDef, tree: ast.AST) -> bool:
        """判断函数是否为类方法"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if func_node in node.body:
                    return True
        return False
    
    def analyze_test_file(self, file_path: Path) -> Dict[str, Any]:
        """分析测试文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            analysis = {
                'file': str(file_path),
                'test_classes': [],
                'test_functions': [],
                'total_tests': 0
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and 'Test' in node.name:
                    test_class = {
                        'name': node.name,
                        'line': node.lineno,
                        'test_methods': []
                    }
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name.startswith('test_'):
                            test_class['test_methods'].append({
                                'name': item.name,
                                'line': item.lineno,
                                'is_async': isinstance(item, ast.AsyncFunctionDef)
                            })
                            analysis['total_tests'] += 1
                    
                    analysis['test_classes'].append(test_class)
                
                elif isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                    analysis['test_functions'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'is_async': isinstance(node, ast.AsyncFunctionDef)
                    })
                    analysis['total_tests'] += 1
            
            return analysis
            
        except Exception as e:
            return {
                'file': str(file_path),
                'error': str(e),
                'test_classes': [],
                'test_functions': [],
                'total_tests': 0
            }
    
    def find_tested_components(self) -> Dict[str, Set[str]]:
        """查找被测试的组件"""
        tested_components = {}
        
        for test_file in self.test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 查找import语句
                imports = []
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            for alias in node.names:
                                imports.append(f"{node.module}.{alias.name}")
                
                tested_components[str(test_file)] = set(imports)
                
            except Exception:
                tested_components[str(test_file)] = set()
        
        return tested_components
    
    def generate_coverage_report(self) -> Dict[str, Any]:
        """生成覆盖率报告"""
        self.scan_project()
        
        # 分析源文件
        source_analysis = {}
        for source_file in self.source_files:
            source_analysis[str(source_file)] = self.analyze_source_file(source_file)
        
        # 分析测试文件
        test_analysis = {}
        for test_file in self.test_files:
            test_analysis[str(test_file)] = self.analyze_test_file(test_file)
        
        # 查找测试覆盖情况
        tested_components = self.find_tested_components()
        
        # 计算统计信息
        total_classes = sum(len(analysis['classes']) for analysis in source_analysis.values())
        total_functions = sum(len(analysis['functions']) for analysis in source_analysis.values())
        total_methods = sum(
            len(cls['methods']) for analysis in source_analysis.values() 
            for cls in analysis['classes']
        )
        total_tests = sum(analysis['total_tests'] for analysis in test_analysis.values())
        total_loc = sum(analysis['lines_of_code'] for analysis in source_analysis.values())
        
        # 估算覆盖率（基于文件名匹配）
        covered_files = set()
        for test_file, imports in tested_components.items():
            for imp in imports:
                for source_file in self.source_files:
                    if source_file.stem in imp or imp in str(source_file):
                        covered_files.add(str(source_file))
        
        file_coverage = len(covered_files) / len(self.source_files) * 100 if self.source_files else 0
        
        report = {
            'summary': {
                'total_source_files': len(self.source_files),
                'total_test_files': len(self.test_files),
                'total_classes': total_classes,
                'total_functions': total_functions,
                'total_methods': total_methods,
                'total_tests': total_tests,
                'total_lines_of_code': total_loc,
                'estimated_file_coverage': file_coverage,
                'test_to_code_ratio': total_tests / (total_classes + total_functions + total_methods) if (total_classes + total_functions + total_methods) > 0 else 0
            },
            'source_files': source_analysis,
            'test_files': test_analysis,
            'tested_components': {k: list(v) for k, v in tested_components.items()},
            'uncovered_files': [str(f) for f in self.source_files if str(f) not in covered_files]
        }
        
        return report
    
    def print_coverage_summary(self, report: Dict[str, Any]):
        """打印覆盖率摘要"""
        summary = report['summary']
        
        print("\n📊 测试覆盖率分析报告")
        print("="*60)
        print(f"源文件数量: {summary['total_source_files']}")
        print(f"测试文件数量: {summary['total_test_files']}")
        print(f"总类数: {summary['total_classes']}")
        print(f"总函数数: {summary['total_functions']}")
        print(f"总方法数: {summary['total_methods']}")
        print(f"总测试数: {summary['total_tests']}")
        print(f"代码行数: {summary['total_lines_of_code']}")
        print(f"估算文件覆盖率: {summary['estimated_file_coverage']:.1f}%")
        print(f"测试代码比: {summary['test_to_code_ratio']:.2f}")
        
        # 显示未覆盖的文件
        if report['uncovered_files']:
            print(f"\n⚠️ 可能未覆盖的文件:")
            for file in report['uncovered_files']:
                print(f"  • {file}")
        
        # 显示测试分布
        print(f"\n📁 测试文件分布:")
        for test_file, analysis in report['test_files'].items():
            test_count = analysis['total_tests']
            print(f"  • {Path(test_file).name}: {test_count} 个测试")


async def main():
    """主函数"""
    print("🔍 快速测试和覆盖率分析")
    
    # 运行快速测试
    try:
        from quick_test import run_quick_test
        success = await run_quick_test()
        
        if not success:
            print("❌ 快速测试失败，请检查测试框架")
            return False
    except Exception as e:
        print(f"❌ 快速测试异常: {e}")
        return False
    
    # 运行覆盖率分析
    print("\n" + "="*60)
    analyzer = CoverageAnalyzer()
    report = analyzer.generate_coverage_report()
    analyzer.print_coverage_summary(report)
    
    # 保存详细报告
    try:
        import json
        with open('reports/coverage_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n📄 详细覆盖率报告已保存: reports/coverage_report.json")
    except Exception as e:
        print(f"⚠️ 保存覆盖率报告失败: {e}")
    
    return True


if __name__ == '__main__':
    # 创建报告目录
    Path("reports").mkdir(exist_ok=True)
    
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n分析被用户中断")
        sys.exit(1)