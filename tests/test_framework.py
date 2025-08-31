#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
自定义测试框架
"""

import asyncio
import functools
import inspect
import traceback
import time
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum


class TestStatus(Enum):
    """测试状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestResult:
    """测试结果数据类"""
    name: str
    status: TestStatus
    duration: float
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None
    assertions: int = 0
    setup_duration: float = 0.0
    teardown_duration: float = 0.0


class AssertionError(Exception):
    """自定义断言错误"""
    pass


class TestCase:
    """测试用例基类"""
    
    def __init__(self):
        self.assertions_count = 0
        self.logger = None
        
    async def setup(self):
        """测试前置操作，子类可重写"""
        pass
    
    async def teardown(self):
        """测试后置操作，子类可重写"""
        pass
    
    def assert_true(self, condition: bool, message: str = ""):
        """断言为真"""
        self.assertions_count += 1
        if not condition:
            raise AssertionError(f"断言失败: {message or '期望为True，实际为False'}")
    
    def assert_false(self, condition: bool, message: str = ""):
        """断言为假"""
        self.assertions_count += 1
        if condition:
            raise AssertionError(f"断言失败: {message or '期望为False，实际为True'}")
    
    def assert_equal(self, actual: Any, expected: Any, message: str = ""):
        """断言相等"""
        self.assertions_count += 1
        if actual != expected:
            raise AssertionError(f"断言失败: {message or f'期望 {expected}，实际 {actual}'}")
    
    def assert_not_equal(self, actual: Any, expected: Any, message: str = ""):
        """断言不相等"""
        self.assertions_count += 1
        if actual == expected:
            raise AssertionError(f"断言失败: {message or f'期望不等于 {expected}，但实际相等'}")
    
    def assert_in(self, item: Any, container: Any, message: str = ""):
        """断言包含"""
        self.assertions_count += 1
        if item not in container:
            raise AssertionError(f"断言失败: {message or f'{item} 不在 {container} 中'}")
    
    def assert_not_in(self, item: Any, container: Any, message: str = ""):
        """断言不包含"""
        self.assertions_count += 1
        if item in container:
            raise AssertionError(f"断言失败: {message or f'{item} 在 {container} 中'}")
    
    def assert_is_none(self, value: Any, message: str = ""):
        """断言为None"""
        self.assertions_count += 1
        if value is not None:
            raise AssertionError(f"断言失败: {message or f'期望None，实际 {value}'}")
    
    def assert_is_not_none(self, value: Any, message: str = ""):
        """断言不为None"""
        self.assertions_count += 1
        if value is None:
            raise AssertionError(f"断言失败: {message or '期望不为None，实际为None'}")
    
    def assert_raises(self, exception_type: type, func: Callable, *args, **kwargs):
        """断言抛出异常"""
        self.assertions_count += 1
        try:
            func(*args, **kwargs)
            raise AssertionError(f"断言失败: 期望抛出 {exception_type.__name__}，但未抛出异常")
        except exception_type:
            pass  # 期望的异常
        except Exception as e:
            raise AssertionError(f"断言失败: 期望抛出 {exception_type.__name__}，实际抛出 {type(e).__name__}: {e}")
    
    async def assert_raises_async(self, exception_type: type, coro: Callable, *args, **kwargs):
        """断言异步函数抛出异常"""
        self.assertions_count += 1
        try:
            await coro(*args, **kwargs)
            raise AssertionError(f"断言失败: 期望抛出 {exception_type.__name__}，但未抛出异常")
        except exception_type:
            pass  # 期望的异常
        except Exception as e:
            raise AssertionError(f"断言失败: 期望抛出 {exception_type.__name__}，实际抛出 {type(e).__name__}: {e}")


class TestSuite:
    """测试套件"""
    
    def __init__(self, name: str = "TestSuite"):
        self.name = name
        self.test_cases: List[TestCase] = []
        self.results: List[TestResult] = []
        self.setup_func: Optional[Callable] = None
        self.teardown_func: Optional[Callable] = None
        
    def add_test_case(self, test_case: TestCase):
        """添加测试用例"""
        self.test_cases.append(test_case)
    
    def setup(self, func: Callable):
        """设置套件前置操作"""
        self.setup_func = func
        return func
    
    def teardown(self, func: Callable):
        """设置套件后置操作"""
        self.teardown_func = func
        return func
    
    async def run(self, logger=None) -> Dict[str, Any]:
        """运行测试套件"""
        if logger:
            logger.info(f"开始运行测试套件: {self.name}")
        
        start_time = time.time()
        
        try:
            # 套件前置操作
            if self.setup_func:
                if asyncio.iscoroutinefunction(self.setup_func):
                    await self.setup_func()
                else:
                    self.setup_func()
            
            # 运行所有测试用例
            for test_case in self.test_cases:
                await self._run_test_case(test_case, logger)
            
            # 套件后置操作
            if self.teardown_func:
                if asyncio.iscoroutinefunction(self.teardown_func):
                    await self.teardown_func()
                else:
                    self.teardown_func()
                    
        except Exception as e:
            if logger:
                logger.error(f"测试套件运行失败: {e}")
        
        duration = time.time() - start_time
        
        # 生成测试报告
        return self._generate_report(duration)
    
    async def _run_test_case(self, test_case: TestCase, logger=None):
        """运行单个测试用例"""
        test_methods = [
            method for method in dir(test_case) 
            if method.startswith('test_') and callable(getattr(test_case, method))
        ]
        
        for method_name in test_methods:
            method = getattr(test_case, method_name)
            test_name = f"{test_case.__class__.__name__}.{method_name}"
            
            if logger:
                logger.debug(f"运行测试: {test_name}")
            
            start_time = time.time()
            result = TestResult(name=test_name, status=TestStatus.RUNNING, duration=0.0)
            
            try:
                # 前置操作
                setup_start = time.time()
                await test_case.setup()
                result.setup_duration = time.time() - setup_start
                
                # 重置断言计数
                test_case.assertions_count = 0
                
                # 执行测试方法
                if asyncio.iscoroutinefunction(method):
                    await method()
                else:
                    method()
                
                result.status = TestStatus.PASSED
                result.assertions = test_case.assertions_count
                
            except AssertionError as e:
                result.status = TestStatus.FAILED
                result.error_message = str(e)
                result.error_traceback = traceback.format_exc()
                
            except Exception as e:
                result.status = TestStatus.ERROR
                result.error_message = str(e)
                result.error_traceback = traceback.format_exc()
                
            finally:
                try:
                    # 后置操作
                    teardown_start = time.time()
                    await test_case.teardown()
                    result.teardown_duration = time.time() - teardown_start
                except Exception as e:
                    if logger:
                        logger.warning(f"测试清理失败: {e}")
                
                result.duration = time.time() - start_time
                self.results.append(result)
                
                if logger:
                    status_symbol = "✅" if result.status == TestStatus.PASSED else "❌"
                    logger.info(f"{status_symbol} {test_name} - {result.status.value} ({result.duration:.3f}s)")
    
    def _generate_report(self, total_duration: float) -> Dict[str, Any]:
        """生成测试报告"""
        total_tests = len(self.results)
        passed = len([r for r in self.results if r.status == TestStatus.PASSED])
        failed = len([r for r in self.results if r.status == TestStatus.FAILED])
        errors = len([r for r in self.results if r.status == TestStatus.ERROR])
        skipped = len([r for r in self.results if r.status == TestStatus.SKIPPED])
        
        return {
            'suite_name': self.name,
            'total_tests': total_tests,
            'passed': passed,
            'failed': failed,
            'errors': errors,
            'skipped': skipped,
            'success_rate': (passed / total_tests * 100) if total_tests > 0 else 0,
            'total_duration': total_duration,
            'results': self.results
        }


class TestRunner:
    """测试运行器"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.suites: List[TestSuite] = []
        
    def add_suite(self, suite: TestSuite):
        """添加测试套件"""
        self.suites.append(suite)
    
    async def run_all(self) -> Dict[str, Any]:
        """运行所有测试套件"""
        if self.logger:
            self.logger.info("开始运行所有测试")
        
        start_time = time.time()
        all_results = []
        
        for suite in self.suites:
            suite_result = await suite.run(self.logger)
            all_results.append(suite_result)
        
        total_duration = time.time() - start_time
        
        # 汇总结果
        summary = self._generate_summary(all_results, total_duration)
        
        # 打印测试报告
        self._print_report(summary)
        
        return summary
    
    def _generate_summary(self, suite_results: List[Dict], total_duration: float) -> Dict[str, Any]:
        """生成汇总报告"""
        total_tests = sum(r['total_tests'] for r in suite_results)
        total_passed = sum(r['passed'] for r in suite_results)
        total_failed = sum(r['failed'] for r in suite_results)
        total_errors = sum(r['errors'] for r in suite_results)
        total_skipped = sum(r['skipped'] for r in suite_results)
        
        return {
            'total_suites': len(suite_results),
            'total_tests': total_tests,
            'total_passed': total_passed,
            'total_failed': total_failed,
            'total_errors': total_errors,
            'total_skipped': total_skipped,
            'overall_success_rate': (total_passed / total_tests * 100) if total_tests > 0 else 0,
            'total_duration': total_duration,
            'suite_results': suite_results
        }
    
    def _print_report(self, summary: Dict[str, Any]):
        """打印测试报告"""
        print("\n" + "="*80)
        print("🧪 测试运行报告")
        print("="*80)
        
        print(f"测试套件数量: {summary['total_suites']}")
        print(f"测试用例总数: {summary['total_tests']}")
        print(f"通过: {summary['total_passed']}")
        print(f"失败: {summary['total_failed']}")
        print(f"错误: {summary['total_errors']}")
        print(f"跳过: {summary['total_skipped']}")
        print(f"成功率: {summary['overall_success_rate']:.1f}%")
        print(f"总耗时: {summary['total_duration']:.3f}秒")
        
        # 详细套件结果
        print("\n📊 套件详情:")
        for suite_result in summary['suite_results']:
            status_icon = "✅" if suite_result['failed'] == 0 and suite_result['errors'] == 0 else "❌"
            print(f"{status_icon} {suite_result['suite_name']}: "
                  f"{suite_result['passed']}/{suite_result['total_tests']} 通过 "
                  f"({suite_result['success_rate']:.1f}%) "
                  f"[{suite_result['total_duration']:.3f}s]")
        
        # 失败的测试详情
        failed_tests = []
        for suite_result in summary['suite_results']:
            for result in suite_result['results']:
                if result.status in [TestStatus.FAILED, TestStatus.ERROR]:
                    failed_tests.append(result)
        
        if failed_tests:
            print("\n❌ 失败的测试:")
            for result in failed_tests:
                print(f"  • {result.name}")
                if result.error_message:
                    print(f"    错误: {result.error_message}")


def test_method(func):
    """测试方法装饰器"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    
    wrapper._is_test = True
    return wrapper


def skip_test(reason: str = ""):
    """跳过测试装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            raise Exception(f"SKIPPED: {reason}")
        wrapper._is_skipped = True
        wrapper._skip_reason = reason
        return wrapper
    return decorator


class MockResponse:
    """模拟HTTP响应"""
    
    def __init__(self, text: str = "", status: int = 200, headers: Dict = None):
        self._text = text
        self.status = status
        self.headers = headers or {}
    
    async def text(self):
        """返回文本内容"""
        return self._text
    
    async def json(self):
        """返回JSON内容"""
        import json
        return json.loads(self._text)


class MockSession:
    """模拟HTTP会话"""
    
    def __init__(self, responses: Dict[str, MockResponse] = None):
        self.responses = responses or {}
        self.requests_made = []
    
    async def request(self, method: str, url: str, **kwargs):
        """模拟请求"""
        self.requests_made.append({'method': method, 'url': url, 'kwargs': kwargs})
        
        if url in self.responses:
            return self.responses[url]
        else:
            return MockResponse("Mock response", 200)
    
    async def get(self, url: str, **kwargs):
        """模拟GET请求"""
        return await self.request('GET', url, **kwargs)
    
    async def post(self, url: str, **kwargs):
        """模拟POST请求"""
        return await self.request('POST', url, **kwargs)


class TestUtils:
    """测试工具类"""
    
    @staticmethod
    def create_temp_file(content: str, suffix: str = ".tmp") -> str:
        """创建临时文件"""
        import tempfile
        import os
        
        fd, path = tempfile.mkstemp(suffix=suffix)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception:
            os.close(fd)
            raise
        
        return path
    
    @staticmethod
    def cleanup_temp_file(path: str):
        """清理临时文件"""
        try:
            import os
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass
    
    @staticmethod
    async def wait_for_condition(condition: Callable, timeout: float = 10.0, interval: float = 0.1) -> bool:
        """等待条件满足"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if asyncio.iscoroutinefunction(condition):
                if await condition():
                    return True
            else:
                if condition():
                    return True
            
            await asyncio.sleep(interval)
        
        return False


# 全局测试运行器实例
_test_runner = TestRunner()


def get_test_runner() -> TestRunner:
    """获取全局测试运行器"""
    return _test_runner


def create_test_suite(name: str) -> TestSuite:
    """创建测试套件"""
    suite = TestSuite(name)
    _test_runner.add_suite(suite)
    return suite