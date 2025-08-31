#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
移动端集成测试脚本
"""

import asyncio
import sys
from utils.logger import setup_logger
from mobile_tools import MobileToolsManager


async def test_mobile_integration():
    """测试移动端集成功能"""
    logger = setup_logger(debug=True)
    manager = MobileToolsManager(logger=logger)
    
    print("🚀 开始移动端集成测试")
    print("="*50)
    
    # 1. 检查环境
    print("\n📋 步骤1: 检查环境")
    checks = await manager.check_environment()
    
    if not all(checks.values()):
        print("\n❌ 环境检查失败，请先完成环境配置")
        print("运行以下命令进行配置:")
        print("python setup_mobile.py")
        return False
    
    print("✅ 环境检查通过")
    
    # 2. 列出AVD
    print("\n📱 步骤2: 检查可用的Android虚拟设备")
    avds = await manager.list_avds()
    
    if not avds:
        print("❌ 未找到可用的AVD")
        print("请创建AVD: python mobile_tools.py create-avd --avd-name test_avd")
        return False
    
    print(f"✅ 找到AVD: {', '.join(avds)}")
    
    # 3. 测试模拟器启动
    print("\n🔧 步骤3: 测试模拟器启动")
    emulator = manager.emulator
    
    test_avd = avds[0]  # 使用第一个可用的AVD
    print(f"正在启动AVD: {test_avd}")
    
    if await emulator.start_emulator(test_avd):
        print("✅ 模拟器启动成功")
        
        # 获取设备信息
        device_info = await emulator.get_device_info()
        if device_info:
            print(f"设备信息: {device_info}")
        
        # 测试截图
        if await emulator.take_screenshot("test_screenshot.png"):
            print("✅ 截图功能正常")
        
        print("\n🧹 清理: 保持模拟器运行以供后续使用")
        # 不关闭模拟器，留给用户使用
        
    else:
        print("❌ 模拟器启动失败")
        return False
    
    print("\n🎉 移动端集成测试完成!")
    print("现在可以运行移动端爬虫:")
    print("python main.py --target mobile_app --mobile --debug")
    
    return True


if __name__ == '__main__':
    try:
        result = asyncio.run(test_mobile_integration())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试过程中出现异常: {e}")
        sys.exit(1)