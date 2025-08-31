#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速测试脚本
"""

import asyncio
import sys
import time
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from tests.test_framework import TestCase, TestSuite, TestRunner, TestStatus
from utils.logger import setup_logger


class QuickTestCase(TestCase):
    """快速测试用例"""
    
    def test_basic_assertions(self):
        """测试基本断言功能"""
        self.assert_true(True, "True应该为真")
        self.assert_false(False, "False应该为假")
        self.assert_equal(1, 1, "1应该等于1")
        self.assert_not_equal(1, 2, "1不应该等于2")
        self.assert_in("test", "testing", "test应该在testing中")
        self.assert_not_in("xyz", "testing", "xyz不应该在testing中")
        self.assert_is_none(None, "None应该为None")
        self.assert_is_not_none("not none", "字符串不应该为None")
    
    def test_exception_assertion(self):
        """测试异常断言"""
        def raise_value_error():
            raise ValueError("Test error")
        
        self.assert_raises(ValueError, raise_value_error)
    
    async def test_async_assertion(self):
        """测试异步断言"""
        async def async_raise_error():
            await asyncio.sleep(0.01)
            raise RuntimeError("Async error")
        
        await self.assert_raises_async(RuntimeError, async_raise_error)
    
    async def test_async_operations(self):
        """测试异步操作"""
        start_time = time.time()
        await asyncio.sleep(0.05)
        duration = time.time() - start_time
        
        self.assert_true(duration >= 0.04, f"异步等待时间应该大于0.04秒，实际: {duration:.3f}秒")


async def run_quick_test():
    """运行快速测试"""
    print("🚀 运行快速测试验证测试框架...")
    
    logger = setup_logger(debug=True)
    
    # 创建测试套件
    suite = TestSuite("Quick Test Suite")
    suite.add_test_case(QuickTestCase())
    
    # 运行测试
    result = await suite.run(logger)
    
    # 显示结果
    print(f"\n📊 测试结果:")
    print(f"总测试数: {result['total_tests']}")
    print(f"通过: {result['passed']}")
    print(f"失败: {result['failed']}")
    print(f"错误: {result['errors']}")
    print(f"成功率: {result['success_rate']:.1f}%")
    print(f"耗时: {result['total_duration']:.3f}秒")
    
    if result['failed'] == 0 and result['errors'] == 0:
        print("\n✅ 测试框架工作正常!")
        return True
    else:
        print("\n❌ 测试框架存在问题!")
        
        # 显示失败详情
        for test_result in result['results']:
            if test_result.status in [TestStatus.FAILED, TestStatus.ERROR]:
                print(f"  ❌ {test_result.name}: {test_result.error_message}")
        
        return False


def main():
    """主函数"""
    print("🧪 爬虫项目测试框架快速验证")
    print("="*50)
    
    try:
        success = asyncio.run(run_quick_test())
        
        if success:
            print("\n🎯 下一步:")
            print("python run_tests.py                    # 运行所有测试")
            print("python run_tests.py --suite spider     # 运行特定套件")
            print("python run_tests.py --performance      # 运行性能测试")
            print("python run_tests.py --verbose          # 详细输出")
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n快速测试异常: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()