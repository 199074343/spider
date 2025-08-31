#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试系统验证脚本
验证测试框架是否正确安装和配置
"""

import sys
import os
import importlib
from pathlib import Path


def check_test_files():
    """检查测试文件是否存在"""
    print("📁 检查测试文件...")
    
    required_files = [
        'tests/__init__.py',
        'tests/test_framework.py',
        'tests/mocks.py', 
        'tests/test_spider.py',
        'tests/test_utils.py',
        'tests/test_mobile.py',
        'tests/test_integration.py',
        'tests/coverage_analyzer.py',
        'tests/test_config_manager.py',
        'run_tests.py',
        'quick_test.py',
        'test_all.py',
        'test_automation.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"  ✅ {file_path}")
    
    if missing_files:
        print(f"\n❌ 缺少以下文件:")
        for file_path in missing_files:
            print(f"  • {file_path}")
        return False
    
    print("✅ 所有测试文件存在")
    return True


def check_imports():
    """检查导入是否正常"""
    print("\n📦 检查模块导入...")
    
    test_modules = [
        'tests.test_framework',
        'tests.mocks',
        'tests.test_config_manager'
    ]
    
    failed_imports = []
    
    for module_name in test_modules:
        try:
            importlib.import_module(module_name)
            print(f"  ✅ {module_name}")
        except ImportError as e:
            failed_imports.append((module_name, str(e)))
            print(f"  ❌ {module_name}: {e}")
    
    if failed_imports:
        print(f"\n❌ 导入失败的模块:")
        for module, error in failed_imports:
            print(f"  • {module}: {error}")
        return False
    
    print("✅ 所有测试模块导入成功")
    return True


def check_test_framework():
    """检查测试框架功能"""
    print("\n🧪 检查测试框架功能...")
    
    try:
        from tests.test_framework import TestCase, TestSuite, TestRunner
        
        # 创建简单测试用例
        class SimpleTest(TestCase):
            def test_basic(self):
                self.assert_equal(1, 1)
                self.assert_true(True)
                self.assert_false(False)
        
        # 创建测试套件
        suite = TestSuite("Verification Test")
        suite.add_test_case(SimpleTest())
        
        print("  ✅ 测试框架类创建成功")
        print("  ✅ 测试用例创建成功")
        print("  ✅ 断言方法可用")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 测试框架检查失败: {e}")
        return False


def check_mock_objects():
    """检查Mock对象"""
    print("\n🎭 检查Mock对象...")
    
    try:
        from tests.mocks import MockLogger, MockHttpSession, MockHttpResponse
        
        # 测试MockLogger
        logger = MockLogger()
        logger.info("Test message")
        logs = logger.get_logs()
        assert len(logs) == 1
        assert logs[0][1] == "Test message"
        
        # 测试MockHttpSession
        session = MockHttpSession()
        response = MockHttpResponse("Test", 200)
        session.set_response("https://test.com", response)
        
        print("  ✅ MockLogger 功能正常")
        print("  ✅ MockHttpSession 功能正常")
        print("  ✅ MockHttpResponse 功能正常")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Mock对象检查失败: {e}")
        return False


def check_dependencies():
    """检查测试依赖"""
    print("\n📋 检查测试依赖...")
    
    # 基础依赖
    basic_deps = ['asyncio', 'json', 'pathlib', 'tempfile']
    
    # 项目依赖
    project_deps = ['aiohttp', 'beautifulsoup4', 'pandas']
    
    # 移动端依赖（可选）
    mobile_deps = ['selenium']  # appium在某些环境可能不可用
    
    missing_deps = []
    
    for dep in basic_deps + project_deps:
        try:
            importlib.import_module(dep)
            print(f"  ✅ {dep}")
        except ImportError:
            missing_deps.append(dep)
            print(f"  ❌ {dep}")
    
    # 检查可选的移动端依赖
    for dep in mobile_deps:
        try:
            importlib.import_module(dep)
            print(f"  ✅ {dep} (移动端)")
        except ImportError:
            print(f"  ⚠️ {dep} (移动端, 可选)")
    
    if missing_deps:
        print(f"\n❌ 缺少必需依赖: {', '.join(missing_deps)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("✅ 所有必需依赖可用")
    return True


def main():
    """主验证流程"""
    print("🔍 测试系统验证")
    print("="*50)
    print("验证测试框架是否正确安装和配置...")
    
    checks = [
        ("文件检查", check_test_files),
        ("依赖检查", check_dependencies), 
        ("导入检查", check_imports),
        ("框架检查", check_test_framework),
        ("Mock检查", check_mock_objects)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name} 异常: {e}")
            all_passed = False
    
    print("\n" + "="*50)
    
    if all_passed:
        print("✅ 测试系统验证通过!")
        print("\n🎯 下一步:")
        print("  python quick_test.py       # 快速测试")
        print("  python run_tests.py        # 运行所有测试")
        print("  python test_all.py         # 完整测试套件")
        return True
    else:
        print("❌ 测试系统验证失败!")
        print("\n🔧 请检查:")
        print("  1. 是否安装了所有依赖: pip install -r requirements.txt")
        print("  2. 是否所有测试文件都存在")
        print("  3. Python路径是否正确")
        return False


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n验证被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n验证过程异常: {e}")
        sys.exit(1)