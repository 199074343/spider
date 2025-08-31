#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
移动端爬虫工具脚本
用于管理Android模拟器和Appium服务
"""

import asyncio
import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict

from utils.logger import setup_logger
from utils.android_emulator import AndroidEmulator


class MobileToolsManager:
    """移动端工具管理器"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.emulator = AndroidEmulator(logger=logger)
    
    async def check_environment(self) -> Dict[str, bool]:
        """检查移动端开发环境"""
        checks = {}
        
        if self.logger:
            self.logger.info("检查移动端开发环境...")
        
        # 检查Android SDK
        try:
            result = subprocess.run(['adb', 'version'], capture_output=True, text=True, timeout=10)
            checks['adb'] = result.returncode == 0
            if checks['adb'] and self.logger:
                self.logger.info("✓ ADB已安装")
        except Exception:
            checks['adb'] = False
            if self.logger:
                self.logger.error("✗ ADB未安装或不在PATH中")
        
        # 检查模拟器
        try:
            result = subprocess.run(['emulator', '-list-avds'], capture_output=True, text=True, timeout=10)
            avds = result.stdout.strip().split('\n') if result.stdout.strip() else []
            checks['emulator'] = len(avds) > 0
            if checks['emulator'] and self.logger:
                self.logger.info(f"✓ 找到 {len(avds)} 个AVD: {', '.join(avds)}")
        except Exception:
            checks['emulator'] = False
            if self.logger:
                self.logger.error("✗ Android模拟器未安装或AVD未创建")
        
        # 检查Appium服务
        try:
            result = subprocess.run(['appium', '--version'], capture_output=True, text=True, timeout=10)
            checks['appium'] = result.returncode == 0
            if checks['appium'] and self.logger:
                self.logger.info("✓ Appium已安装")
        except Exception:
            checks['appium'] = False
            if self.logger:
                self.logger.error("✗ Appium未安装")
        
        # 检查Java
        try:
            result = subprocess.run(['java', '-version'], capture_output=True, text=True, timeout=10)
            checks['java'] = result.returncode == 0
            if checks['java'] and self.logger:
                self.logger.info("✓ Java已安装")
        except Exception:
            checks['java'] = False
            if self.logger:
                self.logger.error("✗ Java未安装")
        
        return checks
    
    async def start_appium_server(self, port: int = 4723) -> bool:
        """启动Appium服务器"""
        try:
            if self.logger:
                self.logger.info(f"启动Appium服务器，端口: {port}")
            
            # 检查端口是否已被占用
            result = subprocess.run(
                ['lsof', '-ti', f':{port}'], 
                capture_output=True, 
                text=True
            )
            
            if result.stdout.strip():
                if self.logger:
                    self.logger.info(f"端口 {port} 已被占用，Appium可能已在运行")
                return True
            
            # 启动Appium服务器
            cmd = ['appium', '--port', str(port), '--allow-cors']
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 等待服务器启动
            max_wait = 30
            wait_time = 0
            
            while wait_time < max_wait:
                try:
                    result = subprocess.run(
                        ['curl', '-s', f'http://localhost:{port}/status'],
                        capture_output=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        if self.logger:
                            self.logger.info(f"Appium服务器启动成功，端口: {port}")
                        return True
                except Exception:
                    pass
                
                await asyncio.sleep(2)
                wait_time += 2
            
            if self.logger:
                self.logger.error("Appium服务器启动超时")
            return False
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"启动Appium服务器失败: {e}")
            return False
    
    async def list_avds(self) -> List[str]:
        """列出可用的AVD"""
        try:
            result = subprocess.run(
                ['emulator', '-list-avds'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                avds = [avd.strip() for avd in result.stdout.strip().split('\n') if avd.strip()]
                return avds
            return []
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"获取AVD列表失败: {e}")
            return []
    
    async def create_avd(self, avd_name: str, package: str = "system-images;android-30;google_apis;x86_64") -> bool:
        """创建新的AVD"""
        try:
            if self.logger:
                self.logger.info(f"创建AVD: {avd_name}")
            
            # 创建AVD
            cmd = [
                'avdmanager', 'create', 'avd',
                '--name', avd_name,
                '--package', package,
                '--device', 'pixel_4'
            ]
            
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 自动回答创建过程中的问题
            stdout, stderr = process.communicate(input='\n')
            
            if process.returncode == 0:
                if self.logger:
                    self.logger.info(f"AVD {avd_name} 创建成功")
                return True
            else:
                if self.logger:
                    self.logger.error(f"创建AVD失败: {stderr}")
                return False
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"创建AVD异常: {e}")
            return False
    
    async def install_app_to_emulator(self, avd_name: str, apk_path: str) -> bool:
        """安装应用到模拟器"""
        try:
            # 启动模拟器
            if not await self.emulator.start_emulator(avd_name):
                return False
            
            # 安装应用
            if not await self.emulator.install_app(apk_path):
                return False
            
            if self.logger:
                self.logger.info(f"应用 {apk_path} 已安装到 {avd_name}")
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"安装应用失败: {e}")
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='移动端爬虫工具')
    parser.add_argument('command', choices=['check', 'start-appium', 'list-avds', 'create-avd', 'install-app'], 
                       help='要执行的命令')
    parser.add_argument('--avd-name', type=str, help='AVD名称')
    parser.add_argument('--apk-path', type=str, help='APK文件路径')
    parser.add_argument('--port', type=int, default=4723, help='Appium服务器端口')
    parser.add_argument('--package', type=str, default="system-images;android-30;google_apis;x86_64", 
                       help='Android系统镜像包')
    parser.add_argument('--debug', action='store_true', help='开启调试模式')
    
    args = parser.parse_args()
    
    logger = setup_logger(debug=args.debug)
    manager = MobileToolsManager(logger=logger)
    
    async def run_command():
        if args.command == 'check':
            checks = await manager.check_environment()
            all_ok = all(checks.values())
            logger.info(f"环境检查完成，状态: {'✓ 全部正常' if all_ok else '✗ 存在问题'}")
            
        elif args.command == 'start-appium':
            await manager.start_appium_server(args.port)
            
        elif args.command == 'list-avds':
            avds = await manager.list_avds()
            if avds:
                logger.info(f"可用的AVD: {', '.join(avds)}")
            else:
                logger.warning("未找到可用的AVD")
                
        elif args.command == 'create-avd':
            if not args.avd_name:
                logger.error("请指定AVD名称 (--avd-name)")
                return
            await manager.create_avd(args.avd_name, args.package)
            
        elif args.command == 'install-app':
            if not args.avd_name or not args.apk_path:
                logger.error("请指定AVD名称 (--avd-name) 和APK路径 (--apk-path)")
                return
            await manager.install_app_to_emulator(args.avd_name, args.apk_path)
    
    try:
        asyncio.run(run_command())
    except KeyboardInterrupt:
        logger.info("操作被用户中断")
    except Exception as e:
        logger.error(f"执行命令失败: {e}")


if __name__ == '__main__':
    main()