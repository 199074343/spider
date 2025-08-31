#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试自动化脚本
支持持续集成和自动化测试
"""

import asyncio
import argparse
import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any

from utils.logger import setup_logger


class TestAutomation:
    """测试自动化管理器"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)
        
    async def run_full_test_suite(self) -> Dict[str, Any]:
        """运行完整测试套件"""
        if self.logger:
            self.logger.info("开始运行完整测试套件...")
        
        start_time = time.time()
        results = {}
        
        # 1. 快速验证测试框架
        if self.logger:
            self.logger.info("步骤1: 验证测试框架")
        
        framework_ok = await self._run_quick_test()
        results['framework_test'] = framework_ok
        
        if not framework_ok:
            if self.logger:
                self.logger.error("测试框架验证失败，停止后续测试")
            return results
        
        # 2. 运行单元测试
        if self.logger:
            self.logger.info("步骤2: 运行单元测试")
        
        unit_tests = await self._run_unit_tests()
        results['unit_tests'] = unit_tests
        
        # 3. 运行集成测试
        if self.logger:
            self.logger.info("步骤3: 运行集成测试")
        
        integration_tests = await self._run_integration_tests()
        results['integration_tests'] = integration_tests
        
        # 4. 运行性能测试
        if self.logger:
            self.logger.info("步骤4: 运行性能测试")
        
        performance_tests = await self._run_performance_tests()
        results['performance_tests'] = performance_tests
        
        # 5. 生成覆盖率报告
        if self.logger:
            self.logger.info("步骤5: 生成覆盖率报告")
        
        coverage_report = await self._generate_coverage_report()
        results['coverage_analysis'] = coverage_report
        
        # 6. 汇总结果
        total_duration = time.time() - start_time
        results['total_duration'] = total_duration
        results['overall_success'] = all([
            framework_ok,
            unit_tests.get('success', False),
            integration_tests.get('success', False),
            performance_tests.get('success', False)
        ])
        
        if self.logger:
            self.logger.info(f"完整测试套件运行完成，耗时: {total_duration:.2f}秒")
        
        return results
    
    async def _run_quick_test(self) -> bool:
        """运行快速测试"""
        try:
            result = subprocess.run([
                sys.executable, 'quick_test.py'
            ], capture_output=True, text=True, timeout=60)
            
            return result.returncode == 0
        except Exception as e:
            if self.logger:
                self.logger.error(f"快速测试失败: {e}")
            return False
    
    async def _run_unit_tests(self) -> Dict[str, Any]:
        """运行单元测试"""
        try:
            result = subprocess.run([
                sys.executable, 'run_tests.py', 
                '--suite', 'spider',
                '--output-format', 'json'
            ], capture_output=True, text=True, timeout=300)
            
            success = result.returncode == 0
            
            return {
                'success': success,
                'output': result.stdout,
                'error': result.stderr if result.stderr else None
            }
        except Exception as e:
            if self.logger:
                self.logger.error(f"单元测试失败: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _run_integration_tests(self) -> Dict[str, Any]:
        """运行集成测试"""
        try:
            result = subprocess.run([
                sys.executable, 'run_tests.py',
                '--suite', 'integration', 
                '--output-format', 'json'
            ], capture_output=True, text=True, timeout=300)
            
            success = result.returncode == 0
            
            return {
                'success': success,
                'output': result.stdout,
                'error': result.stderr if result.stderr else None
            }
        except Exception as e:
            if self.logger:
                self.logger.error(f"集成测试失败: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _run_performance_tests(self) -> Dict[str, Any]:
        """运行性能测试"""
        try:
            result = subprocess.run([
                sys.executable, 'run_tests.py',
                '--performance',
                '--output-format', 'json'
            ], capture_output=True, text=True, timeout=300)
            
            success = result.returncode == 0
            
            return {
                'success': success,
                'output': result.stdout,
                'error': result.stderr if result.stderr else None
            }
        except Exception as e:
            if self.logger:
                self.logger.error(f"性能测试失败: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _generate_coverage_report(self) -> Dict[str, Any]:
        """生成覆盖率报告"""
        try:
            from tests.coverage_analyzer import CoverageAnalyzer
            
            analyzer = CoverageAnalyzer()
            report = analyzer.generate_coverage_report()
            
            # 保存覆盖率报告
            with open(self.reports_dir / 'coverage_report.json', 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            return {
                'success': True,
                'summary': report['summary']
            }
        except Exception as e:
            if self.logger:
                self.logger.error(f"生成覆盖率报告失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def generate_ci_report(self, results: Dict[str, Any]) -> bool:
        """生成CI友好的报告"""
        try:
            ci_report = {
                'timestamp': time.time(),
                'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'overall_success': results.get('overall_success', False),
                'total_duration': results.get('total_duration', 0),
                'test_results': {
                    'framework_test': results.get('framework_test', False),
                    'unit_tests': results.get('unit_tests', {}).get('success', False),
                    'integration_tests': results.get('integration_tests', {}).get('success', False),
                    'performance_tests': results.get('performance_tests', {}).get('success', False)
                },
                'coverage': results.get('coverage_analysis', {}).get('summary', {})
            }
            
            # 保存CI报告
            with open(self.reports_dir / 'ci_report.json', 'w', encoding='utf-8') as f:
                json.dump(ci_report, f, ensure_ascii=False, indent=2)
            
            # 生成简单的状态文件
            status_file = self.reports_dir / 'test_status.txt'
            with open(status_file, 'w') as f:
                f.write("PASS" if results['overall_success'] else "FAIL")
            
            if self.logger:
                self.logger.info(f"CI报告已生成: {self.reports_dir / 'ci_report.json'}")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"生成CI报告失败: {e}")
            return False
    
    def print_automation_summary(self, results: Dict[str, Any]):
        """打印自动化测试摘要"""
        print("\n" + "="*80)
        print("🤖 自动化测试摘要")
        print("="*80)
        
        overall_success = results.get('overall_success', False)
        status_icon = "✅" if overall_success else "❌"
        
        print(f"{status_icon} 总体状态: {'通过' if overall_success else '失败'}")
        print(f"⏱️ 总耗时: {results.get('total_duration', 0):.2f}秒")
        
        print(f"\n📋 测试阶段结果:")
        stages = [
            ('framework_test', '测试框架验证'),
            ('unit_tests', '单元测试'),
            ('integration_tests', '集成测试'),
            ('performance_tests', '性能测试')
        ]
        
        for stage_key, stage_name in stages:
            stage_result = results.get(stage_key)
            if isinstance(stage_result, dict):
                success = stage_result.get('success', False)
            else:
                success = bool(stage_result)
            
            icon = "✅" if success else "❌"
            print(f"  {icon} {stage_name}")
        
        # 覆盖率信息
        coverage = results.get('coverage_analysis', {}).get('summary', {})
        if coverage:
            print(f"\n📊 覆盖率信息:")
            print(f"  文件覆盖率: {coverage.get('estimated_file_coverage', 0):.1f}%")
            print(f"  测试代码比: {coverage.get('test_to_code_ratio', 0):.2f}")
            print(f"  总测试数: {coverage.get('total_tests', 0)}")


async def run_ci_pipeline(args):
    """运行CI管道"""
    logger = setup_logger(debug=args.verbose)
    automation = TestAutomation(logger)
    
    logger.info("🚀 启动CI测试管道")
    
    # 运行完整测试套件
    results = await automation.run_full_test_suite()
    
    # 生成CI报告
    automation.generate_ci_report(results)
    
    # 打印摘要
    automation.print_automation_summary(results)
    
    # 根据结果设置退出码
    return results.get('overall_success', False)


async def run_smoke_tests(args):
    """运行冒烟测试（快速验证）"""
    logger = setup_logger(debug=args.verbose)
    
    logger.info("💨 运行冒烟测试")
    
    try:
        # 只运行核心功能的快速测试
        result = subprocess.run([
            sys.executable, 'quick_test.py'
        ], capture_output=True, text=True, timeout=60)
        
        success = result.returncode == 0
        
        if success:
            logger.info("✅ 冒烟测试通过")
        else:
            logger.error("❌ 冒烟测试失败")
            print(result.stderr)
        
        return success
        
    except Exception as e:
        logger.error(f"冒烟测试异常: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='测试自动化工具')
    parser.add_argument('mode', choices=['ci', 'smoke', 'coverage'], 
                       help='运行模式: ci(完整CI管道), smoke(冒烟测试), coverage(覆盖率分析)')
    parser.add_argument('--verbose', action='store_true', help='详细输出')
    parser.add_argument('--output-dir', type=str, default='reports', help='报告输出目录')
    
    args = parser.parse_args()
    
    # 创建输出目录
    Path(args.output_dir).mkdir(exist_ok=True)
    
    try:
        if args.mode == 'ci':
            success = asyncio.run(run_ci_pipeline(args))
        elif args.mode == 'smoke':
            success = asyncio.run(run_smoke_tests(args))
        elif args.mode == 'coverage':
            from tests.coverage_analyzer import CoverageAnalyzer
            analyzer = CoverageAnalyzer()
            report = analyzer.generate_coverage_report()
            analyzer.print_coverage_summary(report)
            success = True
        else:
            print(f"未知模式: {args.mode}")
            success = False
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试自动化异常: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()