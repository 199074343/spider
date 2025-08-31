#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试运行器主程序
"""

import asyncio
import argparse
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from tests.test_framework import get_test_runner, TestStatus
from utils.logger import setup_logger


class TestReportGenerator:
    """测试报告生成器"""
    
    def __init__(self, logger=None):
        self.logger = logger
    
    def generate_html_report(self, summary: Dict[str, Any], output_path: str = "test_report.html"):
        """生成HTML测试报告"""
        html_content = self._create_html_report(summary)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            if self.logger:
                self.logger.info(f"HTML报告已生成: {output_path}")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"生成HTML报告失败: {e}")
            return False
    
    def generate_json_report(self, summary: Dict[str, Any], output_path: str = "test_report.json"):
        """生成JSON测试报告"""
        try:
            # 转换TestResult对象为字典
            json_summary = self._convert_to_json_serializable(summary)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_summary, f, ensure_ascii=False, indent=2)
            
            if self.logger:
                self.logger.info(f"JSON报告已生成: {output_path}")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"生成JSON报告失败: {e}")
            return False
    
    def _convert_to_json_serializable(self, obj):
        """转换对象为JSON可序列化格式"""
        if hasattr(obj, '__dict__'):
            result = {}
            for key, value in obj.__dict__.items():
                if hasattr(value, 'value'):  # Enum对象
                    result[key] = value.value
                elif isinstance(value, list):
                    result[key] = [self._convert_to_json_serializable(item) for item in value]
                elif hasattr(value, '__dict__'):
                    result[key] = self._convert_to_json_serializable(value)
                else:
                    result[key] = value
            return result
        elif isinstance(obj, list):
            return [self._convert_to_json_serializable(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: self._convert_to_json_serializable(value) for key, value in obj.items()}
        else:
            return obj
    
    def _create_html_report(self, summary: Dict[str, Any]) -> str:
        """创建HTML报告内容"""
        success_rate = summary['overall_success_rate']
        status_color = "green" if success_rate >= 80 else "orange" if success_rate >= 60 else "red"
        
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>爬虫项目测试报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .summary-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .summary-card h3 {{ margin: 0 0 10px 0; color: #333; }}
        .summary-card .value {{ font-size: 2em; font-weight: bold; color: {status_color}; }}
        .suite-results {{ margin-bottom: 30px; }}
        .suite {{ background: #fff; border: 1px solid #ddd; border-radius: 8px; margin-bottom: 20px; }}
        .suite-header {{ background: #f8f9fa; padding: 15px; border-bottom: 1px solid #ddd; font-weight: bold; }}
        .test-result {{ padding: 10px 15px; border-bottom: 1px solid #eee; }}
        .test-result:last-child {{ border-bottom: none; }}
        .status-passed {{ color: green; }}
        .status-failed {{ color: red; }}
        .status-error {{ color: orange; }}
        .status-skipped {{ color: gray; }}
        .error-details {{ background: #fff5f5; border: 1px solid #fed7d7; border-radius: 4px; padding: 10px; margin-top: 5px; font-family: monospace; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 爬虫项目测试报告</h1>
            <p>生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>总测试数</h3>
                <div class="value">{summary['total_tests']}</div>
            </div>
            <div class="summary-card">
                <h3>通过</h3>
                <div class="value" style="color: green;">{summary['total_passed']}</div>
            </div>
            <div class="summary-card">
                <h3>失败</h3>
                <div class="value" style="color: red;">{summary['total_failed']}</div>
            </div>
            <div class="summary-card">
                <h3>错误</h3>
                <div class="value" style="color: orange;">{summary['total_errors']}</div>
            </div>
            <div class="summary-card">
                <h3>成功率</h3>
                <div class="value" style="color: {status_color};">{success_rate:.1f}%</div>
            </div>
            <div class="summary-card">
                <h3>总耗时</h3>
                <div class="value">{summary['total_duration']:.2f}s</div>
            </div>
        </div>
        
        <div class="suite-results">
            <h2>测试套件详情</h2>
"""
        
        # 添加每个套件的详细结果
        for suite_result in summary['suite_results']:
            suite_success_rate = suite_result['success_rate']
            suite_status_color = "green" if suite_success_rate >= 80 else "orange" if suite_success_rate >= 60 else "red"
            
            html += f"""
            <div class="suite">
                <div class="suite-header">
                    📦 {suite_result['suite_name']} 
                    <span style="color: {suite_status_color};">
                        ({suite_result['passed']}/{suite_result['total_tests']} 通过, {suite_success_rate:.1f}%)
                    </span>
                    <span style="float: right;">⏱️ {suite_result['total_duration']:.3f}s</span>
                </div>
"""
            
            # 添加测试结果
            for result in suite_result['results']:
                status_class = f"status-{result.status.value}"
                status_icon = {
                    'passed': '✅',
                    'failed': '❌', 
                    'error': '⚠️',
                    'skipped': '⏭️'
                }.get(result.status.value, '❓')
                
                html += f"""
                <div class="test-result">
                    <span class="{status_class}">{status_icon} {result.name}</span>
                    <span style="float: right;">⏱️ {result.duration:.3f}s | 🔍 {result.assertions} assertions</span>
"""
                
                if result.error_message:
                    html += f"""
                    <div class="error-details">
                        <strong>错误信息:</strong> {result.error_message}
                    </div>
"""
                
                html += "</div>"
            
            html += "</div>"
        
        html += """
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def generate_junit_xml(self, summary: Dict[str, Any], output_path: str = "test_results.xml"):
        """生成JUnit XML格式报告"""
        xml_content = self._create_junit_xml(summary)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            
            if self.logger:
                self.logger.info(f"JUnit XML报告已生成: {output_path}")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"生成JUnit XML报告失败: {e}")
            return False
    
    def _create_junit_xml(self, summary: Dict[str, Any]) -> str:
        """创建JUnit XML内容"""
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += f'<testsuites tests="{summary["total_tests"]}" failures="{summary["total_failed"]}" errors="{summary["total_errors"]}" time="{summary["total_duration"]:.3f}">\n'
        
        for suite_result in summary['suite_results']:
            xml += f'  <testsuite name="{suite_result["suite_name"]}" tests="{suite_result["total_tests"]}" failures="{suite_result["failed"]}" errors="{suite_result["errors"]}" time="{suite_result["total_duration"]:.3f}">\n'
            
            for result in suite_result['results']:
                xml += f'    <testcase name="{result.name}" time="{result.duration:.3f}"'
                
                if result.status == TestStatus.PASSED:
                    xml += '/>\n'
                elif result.status == TestStatus.FAILED:
                    xml += '>\n'
                    xml += f'      <failure message="{self._escape_xml(result.error_message or "")}">{self._escape_xml(result.error_traceback or "")}</failure>\n'
                    xml += '    </testcase>\n'
                elif result.status == TestStatus.ERROR:
                    xml += '>\n'
                    xml += f'      <error message="{self._escape_xml(result.error_message or "")}">{self._escape_xml(result.error_traceback or "")}</error>\n'
                    xml += '    </testcase>\n'
                elif result.status == TestStatus.SKIPPED:
                    xml += '>\n'
                    xml += '      <skipped/>\n'
                    xml += '    </testcase>\n'
            
            xml += '  </testsuite>\n'
        
        xml += '</testsuites>\n'
        return xml
    
    def _escape_xml(self, text: str) -> str:
        """转义XML特殊字符"""
        if not text:
            return ""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#39;'))


async def run_all_tests(args):
    """运行所有测试"""
    logger = setup_logger(debug=args.verbose)
    
    # 导入所有测试模块
    try:
        import tests.test_spider
        import tests.test_utils
        import tests.test_mobile
        import tests.test_integration
        
        if logger:
            logger.info("所有测试模块加载成功")
            
    except ImportError as e:
        if logger:
            logger.error(f"导入测试模块失败: {e}")
        return False
    
    # 获取测试运行器
    runner = get_test_runner()
    runner.logger = logger
    
    # 运行所有测试
    summary = await runner.run_all()
    
    # 生成报告
    if args.output_format in ['html', 'all']:
        report_generator = TestReportGenerator(logger)
        report_generator.generate_html_report(summary, "reports/test_report.html")
    
    if args.output_format in ['json', 'all']:
        report_generator = TestReportGenerator(logger)
        report_generator.generate_json_report(summary, "reports/test_report.json")
    
    if args.output_format in ['junit', 'all']:
        report_generator = TestReportGenerator(logger)
        report_generator.generate_junit_xml(summary, "reports/test_results.xml")
    
    # 返回测试是否全部通过
    return summary['total_failed'] == 0 and summary['total_errors'] == 0


async def run_specific_suite(suite_name: str, args):
    """运行特定测试套件"""
    logger = setup_logger(debug=args.verbose)
    
    # 导入对应的测试模块
    suite_modules = {
        'spider': 'tests.test_spider',
        'utils': 'tests.test_utils', 
        'mobile': 'tests.test_mobile',
        'integration': 'tests.test_integration'
    }
    
    if suite_name not in suite_modules:
        logger.error(f"未知的测试套件: {suite_name}")
        return False
    
    try:
        __import__(suite_modules[suite_name])
        logger.info(f"测试套件 {suite_name} 加载成功")
    except ImportError as e:
        logger.error(f"导入测试套件失败: {e}")
        return False
    
    # 运行指定套件
    runner = get_test_runner()
    runner.logger = logger
    
    # 只运行指定套件
    target_suite = None
    for suite in runner.suites:
        if suite_name.lower() in suite.name.lower():
            target_suite = suite
            break
    
    if not target_suite:
        logger.error(f"未找到测试套件: {suite_name}")
        return False
    
    # 临时清空其他套件
    original_suites = runner.suites.copy()
    runner.suites = [target_suite]
    
    try:
        summary = await runner.run_all()
        return summary['total_failed'] == 0 and summary['total_errors'] == 0
    finally:
        runner.suites = original_suites


async def run_performance_tests(args):
    """运行性能测试"""
    logger = setup_logger(debug=args.verbose)
    logger.info("运行性能测试...")
    
    # 这里可以添加专门的性能测试
    # 目前在integration测试中包含了基本的性能测试
    
    try:
        import tests.test_integration
        runner = get_test_runner()
        runner.logger = logger
        
        # 只运行性能相关的测试
        for suite in runner.suites:
            if "integration" in suite.name.lower():
                summary = await suite.run(logger)
                
                # 检查性能测试结果
                perf_tests = [r for r in summary['results'] if 'performance' in r.name.lower()]
                if perf_tests:
                    logger.info(f"性能测试完成: {len(perf_tests)} 个测试")
                    for test in perf_tests:
                        logger.info(f"  {test.name}: {test.duration:.3f}s")
                
                return summary['failed'] == 0 and summary['errors'] == 0
        
        logger.warning("未找到性能测试")
        return True
        
    except Exception as e:
        logger.error(f"性能测试失败: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='爬虫项目测试运行器')
    parser.add_argument('--suite', type=str, help='运行特定测试套件 (spider, utils, mobile, integration)')
    parser.add_argument('--performance', action='store_true', help='只运行性能测试')
    parser.add_argument('--output-format', choices=['html', 'json', 'junit', 'all'], 
                       default='html', help='报告输出格式')
    parser.add_argument('--verbose', action='store_true', help='详细输出')
    parser.add_argument('--reports-dir', type=str, default='reports', help='报告输出目录')
    
    args = parser.parse_args()
    
    # 创建报告目录
    Path(args.reports_dir).mkdir(exist_ok=True)
    
    # 更新报告路径
    if hasattr(args, 'reports_dir') and args.reports_dir != 'reports':
        # 这里可以动态调整报告路径
        pass
    
    try:
        if args.performance:
            # 运行性能测试
            success = asyncio.run(run_performance_tests(args))
        elif args.suite:
            # 运行特定套件
            success = asyncio.run(run_specific_suite(args.suite, args))
        else:
            # 运行所有测试
            success = asyncio.run(run_all_tests(args))
        
        if success:
            print("\n🎉 所有测试通过!")
            sys.exit(0)
        else:
            print("\n❌ 测试失败!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试运行异常: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()