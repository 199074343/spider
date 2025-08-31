#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
移动端环境安装和设置脚本
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description=""):
    """运行命令并显示结果"""
    print(f"\n{'='*50}")
    print(f"执行: {description}")
    print(f"命令: {' '.join(cmd)}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✓ 成功")
        if result.stdout:
            print(f"输出: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 失败: {e}")
        if e.stderr:
            print(f"错误: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"✗ 命令未找到: {cmd[0]}")
        return False


def check_prerequisites():
    """检查前置条件"""
    print("检查前置条件...")
    
    checks = {
        'python': ['python3', '--version'],
        'java': ['java', '-version'],
        'node': ['node', '--version'],
        'npm': ['npm', '--version']
    }
    
    all_ok = True
    for name, cmd in checks.items():
        if not run_command(cmd, f"检查 {name}"):
            all_ok = False
    
    return all_ok


def install_python_dependencies():
    """安装Python依赖"""
    print("\n安装Python依赖...")
    return run_command([
        sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
    ], "安装Python包")


def install_appium():
    """安装Appium"""
    print("\n安装Appium...")
    
    # 安装Appium
    if not run_command(['npm', 'install', '-g', 'appium'], "安装Appium"):
        return False
    
    # 安装UiAutomator2驱动
    if not run_command(['appium', 'driver', 'install', 'uiautomator2'], "安装UiAutomator2驱动"):
        return False
    
    return True


def setup_android_sdk():
    """设置Android SDK提示"""
    print("\n" + "="*60)
    print("Android SDK 设置说明")
    print("="*60)
    print("""
请按照以下步骤设置Android SDK:

1. 下载Android Studio: https://developer.android.com/studio
2. 安装Android Studio并启动
3. 通过SDK Manager安装以下组件:
   - Android SDK Platform-Tools
   - Android SDK Build-Tools
   - Android Emulator
   - 至少一个Android API Level (推荐API 30+)

4. 设置环境变量:
   export ANDROID_HOME=$HOME/Android/Sdk
   export PATH=$PATH:$ANDROID_HOME/emulator
   export PATH=$PATH:$ANDROID_HOME/platform-tools
   export PATH=$PATH:$ANDROID_HOME/tools/bin

5. 创建AVD (Android Virtual Device):
   - 打开Android Studio
   - 进入 Tools > AVD Manager
   - 创建新的虚拟设备
   - 或使用命令: python mobile_tools.py create-avd --avd-name test_avd

6. 验证安装:
   python mobile_tools.py check
""")


def create_directories():
    """创建必要的目录"""
    directories = ['screenshots', 'mobile_data', 'mobile_browser_data', 'logs']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ 创建目录: {directory}")


def main():
    """主安装流程"""
    print("移动端爬虫环境安装向导")
    print("="*50)
    
    # 检查前置条件
    if not check_prerequisites():
        print("\n❌ 前置条件检查失败，请先安装缺失的软件")
        return False
    
    # 创建目录
    create_directories()
    
    # 安装Python依赖
    if not install_python_dependencies():
        print("\n❌ Python依赖安装失败")
        return False
    
    # 安装Appium
    if not install_appium():
        print("\n❌ Appium安装失败")
        return False
    
    # Android SDK设置说明
    setup_android_sdk()
    
    print("\n" + "="*60)
    print("安装完成！")
    print("="*60)
    print("""
后续步骤:
1. 按照上述说明设置Android SDK
2. 创建AVD: python mobile_tools.py create-avd --avd-name test_avd
3. 检查环境: python mobile_tools.py check
4. 启动Appium: python mobile_tools.py start-appium
5. 运行移动端爬虫: python main.py --target mobile_app --mobile --debug

示例命令:
# 检查环境
python mobile_tools.py check

# 启动Appium服务器
python mobile_tools.py start-appium

# 运行移动应用爬虫
python main.py --target mobile_app --mobile --debug

# 运行移动浏览器爬虫
python main.py --target mobile_browser --mobile --debug

# 直接运行示例
python example_mobile_spider.py
python example_mobile_spider.py browser
""")
    
    return True


if __name__ == '__main__':
    main()