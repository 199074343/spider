#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Appium移动端自动化处理器
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class AppiumHandler:
    """Appium自动化处理器"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.driver = None
        self.capabilities = {}
        
    async def setup_driver(self, device_config: Dict[str, Any]) -> bool:
        """设置Appium驱动"""
        try:
            # 设置Appium capabilities
            options = UiAutomator2Options()
            
            # 基本配置
            options.platform_name = device_config.get('platformName', 'Android')
            options.platform_version = device_config.get('platformVersion', '11.0')
            options.device_name = device_config.get('deviceName', 'emulator-5554')
            options.automation_name = device_config.get('automationName', 'UiAutomator2')
            
            # 应用配置
            if 'appPackage' in device_config:
                options.app_package = device_config['appPackage']
            if 'appActivity' in device_config:
                options.app_activity = device_config['appActivity']
            if 'appPath' in device_config:
                options.app = device_config['appPath']
            
            # 其他配置
            options.no_reset = device_config.get('noReset', True)
            options.full_reset = device_config.get('fullReset', False)
            options.new_command_timeout = device_config.get('newCommandTimeout', 300)
            
            # 连接到Appium服务器
            appium_server_url = device_config.get('appiumServerUrl', 'http://localhost:4723')
            
            if self.logger:
                self.logger.info(f"正在连接Appium服务器: {appium_server_url}")
            
            # 在线程池中创建驱动（避免阻塞）
            self.driver = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: webdriver.Remote(appium_server_url, options=options)
            )
            
            if self.logger:
                self.logger.info("Appium驱动创建成功")
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"设置Appium驱动失败: {e}")
            return False
    
    async def find_element(self, by: str, value: str, timeout: int = 10):
        """查找元素"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: wait.until(EC.presence_of_element_located((by, value)))
            )
            return element
        except TimeoutException:
            if self.logger:
                self.logger.warning(f"未找到元素: {by}={value}")
            return None
        except Exception as e:
            if self.logger:
                self.logger.error(f"查找元素失败: {e}")
            return None
    
    async def find_elements(self, by: str, value: str, timeout: int = 10) -> List:
        """查找多个元素"""
        try:
            await asyncio.sleep(1)  # 等待页面加载
            elements = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.driver.find_elements(by, value)
            )
            return elements
        except Exception as e:
            if self.logger:
                self.logger.error(f"查找元素列表失败: {e}")
            return []
    
    async def click_element(self, by: str, value: str, timeout: int = 10) -> bool:
        """点击元素"""
        try:
            element = await self.find_element(by, value, timeout)
            if element:
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    element.click
                )
                if self.logger:
                    self.logger.debug(f"点击元素: {by}={value}")
                return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"点击元素失败: {e}")
        return False
    
    async def input_text(self, by: str, value: str, text: str, timeout: int = 10) -> bool:
        """输入文本"""
        try:
            element = await self.find_element(by, value, timeout)
            if element:
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: element.clear()
                )
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: element.send_keys(text)
                )
                if self.logger:
                    self.logger.debug(f"输入文本到 {by}={value}: {text}")
                return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"输入文本失败: {e}")
        return False
    
    async def get_text(self, by: str, value: str, timeout: int = 10) -> str:
        """获取元素文本"""
        try:
            element = await self.find_element(by, value, timeout)
            if element:
                text = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: element.text
                )
                return text
        except Exception as e:
            if self.logger:
                self.logger.error(f"获取文本失败: {e}")
        return ""
    
    async def scroll_down(self, duration: int = 1000) -> bool:
        """向下滚动"""
        try:
            size = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.driver.get_window_size()
            )
            
            start_x = size['width'] // 2
            start_y = size['height'] * 0.8
            end_y = size['height'] * 0.2
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.driver.swipe(start_x, start_y, start_x, end_y, duration)
            )
            
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"滚动失败: {e}")
            return False
    
    async def get_page_source(self) -> str:
        """获取页面源码"""
        try:
            source = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.driver.page_source
            )
            return source
        except Exception as e:
            if self.logger:
                self.logger.error(f"获取页面源码失败: {e}")
            return ""
    
    async def take_screenshot(self, save_path: str = "mobile_screenshot.png") -> bool:
        """截取移动端截图"""
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.driver.save_screenshot(save_path)
            )
            
            if self.logger:
                self.logger.info(f"移动端截图已保存: {save_path}")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"移动端截图失败: {e}")
            return False
    
    async def wait_for_element(self, by: str, value: str, timeout: int = 30) -> bool:
        """等待元素出现"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: wait.until(EC.presence_of_element_located((by, value)))
            )
            return True
        except TimeoutException:
            if self.logger:
                self.logger.warning(f"等待元素超时: {by}={value}")
            return False
        except Exception as e:
            if self.logger:
                self.logger.error(f"等待元素失败: {e}")
            return False
    
    async def execute_adb_command(self, command: str) -> str:
        """执行ADB命令"""
        try:
            if not self.device:
                await self.connect_device()
            
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                self.device.shell,
                command
            )
            
            return result
        except Exception as e:
            if self.logger:
                self.logger.error(f"执行ADB命令失败: {e}")
            return ""
    
    async def close(self):
        """关闭驱动"""
        try:
            if self.driver:
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.driver.quit
                )
                if self.logger:
                    self.logger.info("Appium驱动已关闭")
        except Exception as e:
            if self.logger:
                self.logger.error(f"关闭驱动失败: {e}")