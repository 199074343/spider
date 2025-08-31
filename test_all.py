#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完整测试启动脚本
一键运行所有测试并生成完整报告
"""

import asyncio
import sys
import time
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import setup_logger


async def main():
    """主函数"""
    print("🧪 爬虫项目完整测试套件")
    print("="*60)
    print("这将运行所有测试并生成完整的测试报告")
    print("="*60)
    
    logger = setup_logger(debug=True)
    
    # 创建必要的目录
    Path("reports").mkdir(exist_ok=True)
    Path("screenshots").mkdir(exist_ok=True)
    
    start_time = time.time()
    
    try:
        # 1. 快速验证
        print("\n🚀 步骤1: 快速验证测试框架")
        print("-" * 40)
        
        from quick_test import run_quick_test
        framework_ok = await run_quick_test()
        
        if not framework_ok:
            print("❌ 测试框架验证失败，请检查环境")
            return False
        
        # 2. 运行所有测试套件
        print("\n🧪 步骤2: 运行完整测试套件")
        print("-" * 40)
        
        # 导入所有测试模块
        import tests.test_spider
        import tests.test_utils  
        import tests.test_mobile
        import tests.test_integration
        
        from tests.test_framework import get_test_runner
        
        runner = get_test_runner()
        runner.logger = logger
        
        # 运行所有测试
        summary = await runner.run_all()
        
        # 3. 生成报告
        print("\n📊 步骤3: 生成测试报告")
        print("-" * 40)
        
        from run_tests import TestReportGenerator
        report_generator = TestReportGenerator(logger)
        
        # 生成多种格式的报告
        report_generator.generate_html_report(summary, "reports/test_report.html")
        report_generator.generate_json_report(summary, "reports/test_report.json")
        report_generator.generate_junit_xml(summary, "reports/test_results.xml")
        
        # 4. 覆盖率分析
        print("\n📈 步骤4: 覆盖率分析")
        print("-" * 40)
        
        from tests.coverage_analyzer import CoverageAnalyzer
        analyzer = CoverageAnalyzer()
        coverage_report = analyzer.generate_coverage_report()
        analyzer.print_coverage_summary(coverage_report)
        
        # 保存覆盖率报告
        import json
        with open('reports/coverage_report.json', 'w', encoding='utf-8') as f:
            json.dump(coverage_report, f, ensure_ascii=False, indent=2)
        
        # 5. 最终总结
        total_duration = time.time() - start_time
        
        print("\n" + "="*60)
        print("🎯 测试完成总结")
        print("="*60)
        
        print(f"📊 测试统计:")
        print(f"  • 总测试数: {summary['total_tests']}")
        print(f"  • 通过: {summary['total_passed']}")
        print(f"  • 失败: {summary['total_failed']}")
        print(f"  • 错误: {summary['total_errors']}")
        print(f"  • 成功率: {summary['overall_success_rate']:.1f}%")
        print(f"  • 总耗时: {total_duration:.2f}秒")
        
        print(f"\n📁 生成的报告:")
        print(f"  • HTML报告: reports/test_report.html")
        print(f"  • JSON报告: reports/test_report.json")
        print(f"  • JUnit XML: reports/test_results.xml")
        print(f"  • 覆盖率报告: reports/coverage_report.json")
        
        # 覆盖率摘要
        coverage_summary = coverage_report['summary']
        print(f"\n📈 覆盖率摘要:")
        print(f"  • 文件覆盖率: {coverage_summary['estimated_file_coverage']:.1f}%")
        print(f"  • 测试代码比: {coverage_summary['test_to_code_ratio']:.2f}")
        print(f"  • 代码行数: {coverage_summary['total_lines_of_code']}")
        
        # 判断整体成功
        overall_success = (
            summary['total_failed'] == 0 and 
            summary['total_errors'] == 0 and
            summary['overall_success_rate'] >= 80
        )
        
        if overall_success:
            print(f"\n✅ 所有测试通过! 项目质量良好。")
        else:
            print(f"\n❌ 存在测试失败或成功率不足80%")
            
            # 显示失败的测试
            if summary['total_failed'] > 0 or summary['total_errors'] > 0:
                print(f"\n❌ 失败的测试:")
                for suite_result in summary['suite_results']:
                    for result in suite_result['results']:
                        if result.status.value in ['failed', 'error']:
                            print(f"  • {result.name}: {result.error_message}")
        
        return overall_success
        
    except Exception as e:
        logger.error(f"测试运行异常: {e}")
        print(f"\n💥 测试运行过程中发生异常: {e}")
        return False


if __name__ == '__main__':
    try:
        success = asyncio.run(main())
        
        print(f"\n{'='*60}")
        if success:
            print("🎉 测试套件运行成功!")
            print("\n💡 提示:")
            print("  • 查看 reports/test_report.html 获取详细测试报告")
            print("  • 运行 python run_tests.py --help 查看更多测试选项")
            print("  • 运行 python test_automation.py ci 进行CI模式测试")
        else:
            print("❌ 测试套件运行失败!")
            print("\n🔧 故障排除:")
            print("  • 检查 reports/ 目录中的详细报告")
            print("  • 运行 python quick_test.py 验证基础功能")
            print("  • 使用 --verbose 参数获取详细日志")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试启动异常: {e}")
        sys.exit(1)