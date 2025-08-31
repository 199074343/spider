#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Android模拟器集成模块
"""

import asyncio
import subprocess
import time
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import adb_shell
from adb_shell.adb_device import AdbDeviceTcp, AdbDeviceUsb


class AndroidEmulator:
    """Android模拟器管理器"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.emulator_name = None
        self.device = None
        self.adb_port = 5555
        self.emulator_port = 5554
        
    async def start_emulator(self, avd_name: str, port: int = 5554) -> bool:
        """启动Android模拟器"""
        try:
            self.emulator_name = avd_name
            self.emulator_port = port
            self.adb_port = port + 1
            
            if self.logger:
                self.logger.info(f"正在启动模拟器: {avd_name}")
            
            # 检查模拟器是否已经运行
            if await self._is_emulator_running():
                if self.logger:
                    self.logger.info("模拟器已经在运行")
                return True
            
            # 启动模拟器
            cmd = [
                "emulator", "-avd", avd_name, 
                "-port", str(port),
                "-no-audio", "-no-window"  # 无界面模式
            ]
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # 等待模拟器启动
            max_wait = 120  # 最大等待2分钟
            wait_time = 0
            
            while wait_time < max_wait:
                if await self._is_emulator_running():
                    if self.logger:
                        self.logger.info(f"模拟器启动成功，耗时: {wait_time}秒")
                    return True
                
                await asyncio.sleep(5)
                wait_time += 5
                
                if self.logger and wait_time % 30 == 0:
                    self.logger.info(f"等待模拟器启动... ({wait_time}s)")
            
            if self.logger:
                self.logger.error("模拟器启动超时")
            return False
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"启动模拟器失败: {e}")
            return False
    
    async def _is_emulator_running(self) -> bool:
        """检查模拟器是否正在运行"""
        try:
            result = subprocess.run(
                ["adb", "devices"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            return f"emulator-{self.emulator_port}" in result.stdout
            
        except Exception:
            return False
    
    async def connect_device(self) -> bool:
        """连接到模拟器设备"""
        try:
            device_id = f"127.0.0.1:{self.adb_port}"
            
            # 连接ADB设备
            self.device = AdbDeviceTcp(host="127.0.0.1", port=self.adb_port, default_timeout_s=30)
            await asyncio.get_event_loop().run_in_executor(None, self.device.connect)
            
            if self.logger:
                self.logger.info(f"成功连接到设备: {device_id}")
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"连接设备失败: {e}")
            return False
    
    async def install_app(self, apk_path: str) -> bool:
        """安装APK应用"""
        try:
            if not self.device:
                await self.connect_device()
            
            if self.logger:
                self.logger.info(f"正在安装应用: {apk_path}")
            
            # 使用adb安装APK
            result = await asyncio.get_event_loop().run_in_executor(
                None, 
                self.device.shell, 
                f"pm install {apk_path}"
            )
            
            if "Success" in result:
                if self.logger:
                    self.logger.info("应用安装成功")
                return True
            else:
                if self.logger:
                    self.logger.error(f"应用安装失败: {result}")
                return False
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"安装应用时出错: {e}")
            return False
    
    async def launch_app(self, package_name: str, activity_name: str = None) -> bool:
        """启动应用"""
        try:
            if not self.device:
                await self.connect_device()
            
            if activity_name:
                launch_cmd = f"am start -n {package_name}/{activity_name}"
            else:
                launch_cmd = f"monkey -p {package_name} -c android.intent.category.LAUNCHER 1"
            
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                self.device.shell,
                launch_cmd
            )
            
            if self.logger:
                self.logger.info(f"启动应用: {package_name}")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"启动应用失败: {e}")
            return False
    
    async def take_screenshot(self, save_path: str = "screenshot.png") -> bool:
        """截取屏幕截图"""
        try:
            if not self.device:
                await self.connect_device()
            
            # 截图命令
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                self.device.shell,
                "screencap -p /sdcard/screenshot.png"
            )
            
            # 拉取截图文件
            pull_result = await asyncio.get_event_loop().run_in_executor(
                None,
                self.device.pull,
                "/sdcard/screenshot.png",
                save_path
            )
            
            if self.logger:
                self.logger.info(f"截图已保存到: {save_path}")
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"截图失败: {e}")
            return False
    
    async def get_device_info(self) -> Dict[str, str]:
        """获取设备信息"""
        try:
            if not self.device:
                await self.connect_device()
            
            info = {}
            
            # 获取设备属性
            properties = [
                ("ro.product.model", "model"),
                ("ro.build.version.release", "android_version"),
                ("ro.product.manufacturer", "manufacturer"),
                ("ro.build.version.sdk", "sdk_version")
            ]
            
            for prop, key in properties:
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.device.shell,
                    f"getprop {prop}"
                )
                info[key] = result.strip()
            
            return info
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"获取设备信息失败: {e}")
            return {}
    
    async def stop_emulator(self) -> bool:
        """停止模拟器"""
        try:
            if self.device:
                self.device.close()
            
            # 关闭模拟器
            result = subprocess.run(
                ["adb", "-s", f"emulator-{self.emulator_port}", "emu", "kill"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if self.logger:
                self.logger.info("模拟器已停止")
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"停止模拟器失败: {e}")
            return False
    
    async def list_installed_apps(self) -> List[str]:
        """列出已安装的应用"""
        try:
            if not self.device:
                await self.connect_device()
            
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                self.device.shell,
                "pm list packages -3"  # 只列出第三方应用
            )
            
            packages = []
            for line in result.split('\n'):
                if line.startswith('package:'):
                    package_name = line.replace('package:', '').strip()
                    packages.append(package_name)
            
            return packages
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"获取应用列表失败: {e}")
            return []