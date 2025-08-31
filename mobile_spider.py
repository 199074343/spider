#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
移动端爬虫基类
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from selenium.webdriver.common.by import By

from spider import Spider, SpiderConfig
from utils.android_emulator import AndroidEmulator
from utils.appium_handler import AppiumHandler
from utils.data_processor import DataProcessor
from utils.storage import Storage


@dataclass
class MobileSpiderConfig(SpiderConfig):
    """移动端爬虫配置类"""
    # Android模拟器配置
    avd_name: str = "test_avd"
    emulator_port: int = 5554
    
    # Appium配置
    appium_server_url: str = "http://localhost:4723"
    platform_name: str = "Android"
    platform_version: str = "11.0"
    device_name: str = "emulator-5554"
    automation_name: str = "UiAutomator2"
    
    # 应用配置
    app_package: Optional[str] = None
    app_activity: Optional[str] = None
    app_path: Optional[str] = None
    
    # 移动端特定配置
    no_reset: bool = True
    full_reset: bool = False
    new_command_timeout: int = 300
    implicit_wait: int = 10
    page_load_timeout: int = 30


class MobileSpider(Spider):
    """移动端爬虫基类"""
    
    def __init__(self, target: str, config_path: str = 'config.json', 
                 workers: int = 1, logger=None):  # 移动端通常单线程
        super().__init__(target, config_path, workers, logger)
        self.emulator = AndroidEmulator(logger=logger)
        self.appium_handler = AppiumHandler(logger=logger)
        self.mobile_config = self._load_mobile_config()
        
    def _load_mobile_config(self) -> MobileSpiderConfig:
        """加载移动端配置"""
        try:
            config_path = 'config.json'  # 使用默认配置文件路径
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                
            target_config = config_data.get(self.target, {})
            
            # 合并基础配置和移动端配置
            base_config = self.config.__dict__
            mobile_config_dict = {**base_config, **target_config}
            
            return MobileSpiderConfig(**mobile_config_dict)
        except Exception as e:
            if self.logger:
                self.logger.error(f"加载移动端配置失败: {e}")
            # 返回默认配置
            return MobileSpiderConfig(
                target=self.target,
                base_url="",
                headers={}
            )
    
    async def setup_mobile_environment(self) -> bool:
        """设置移动端环境"""
        try:
            if self.logger:
                self.logger.info("正在设置移动端环境...")
            
            # 1. 启动Android模拟器
            if not await self.emulator.start_emulator(
                self.mobile_config.avd_name, 
                self.mobile_config.emulator_port
            ):
                return False
            
            # 2. 连接设备
            if not await self.emulator.connect_device():
                return False
            
            # 3. 获取设备信息
            device_info = await self.emulator.get_device_info()
            if self.logger:
                self.logger.info(f"设备信息: {device_info}")
            
            # 4. 设置Appium驱动
            device_config = {
                'platformName': self.mobile_config.platform_name,
                'platformVersion': device_info.get('android_version', self.mobile_config.platform_version),
                'deviceName': self.mobile_config.device_name,
                'automationName': self.mobile_config.automation_name,
                'appiumServerUrl': self.mobile_config.appium_server_url,
                'noReset': self.mobile_config.no_reset,
                'fullReset': self.mobile_config.full_reset,
                'newCommandTimeout': self.mobile_config.new_command_timeout
            }
            
            # 添加应用配置
            if self.mobile_config.app_package:
                device_config['appPackage'] = self.mobile_config.app_package
            if self.mobile_config.app_activity:
                device_config['appActivity'] = self.mobile_config.app_activity
            if self.mobile_config.app_path:
                device_config['appPath'] = self.mobile_config.app_path
            
            if not await self.appium_handler.setup_driver(device_config):
                return False
            
            if self.logger:
                self.logger.info("移动端环境设置完成")
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"设置移动端环境失败: {e}")
            return False
    
    async def run(self):
        """运行移动端爬虫"""
        try:
            if self.logger:
                self.logger.info(f"开始移动端爬取: {self.target}")
            
            # 设置移动端环境
            if not await self.setup_mobile_environment():
                if self.logger:
                    self.logger.error("移动端环境设置失败")
                return
            
            # 等待应用启动
            await asyncio.sleep(5)
            
            # 执行移动端爬取任务
            results = await self.execute_mobile_tasks()
            
            # 保存结果
            if results:
                await self.save_results(results)
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"移动端爬虫运行失败: {e}")
        finally:
            # 清理资源
            await self.cleanup()
    
    async def execute_mobile_tasks(self) -> List[Dict[str, Any]]:
        """执行移动端爬取任务，子类应重写此方法"""
        results = []
        
        try:
            # 默认实现：获取当前页面信息
            page_source = await self.appium_handler.get_page_source()
            screenshot_path = f"screenshots/{self.target}_mobile.png"
            
            # 创建截图目录
            Path("screenshots").mkdir(exist_ok=True)
            await self.appium_handler.take_screenshot(screenshot_path)
            
            result = {
                'target': self.target,
                'page_source': page_source,
                'screenshot': screenshot_path,
                'timestamp': time.time()
            }
            
            results.append(result)
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"执行移动端任务失败: {e}")
        
        return results
    
    async def navigate_to_url(self, url: str) -> bool:
        """导航到指定URL（适用于移动浏览器）"""
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.appium_handler.driver.get(url)
            )
            
            # 等待页面加载
            await asyncio.sleep(3)
            
            if self.logger:
                self.logger.info(f"导航到URL: {url}")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"导航失败: {e}")
            return False
    
    async def wait_and_click(self, by: str, value: str, timeout: int = 10) -> bool:
        """等待并点击元素"""
        if await self.appium_handler.wait_for_element(by, value, timeout):
            return await self.appium_handler.click_element(by, value)
        return False
    
    async def extract_list_data(self, list_selector: str, item_selectors: Dict[str, str]) -> List[Dict[str, Any]]:
        """提取列表数据"""
        results = []
        
        try:
            # 查找列表元素
            list_elements = await self.appium_handler.find_elements(By.XPATH, list_selector)
            
            if self.logger:
                self.logger.info(f"找到 {len(list_elements)} 个列表项")
            
            for i, element in enumerate(list_elements):
                item_data = {'index': i}
                
                # 提取每个项目的数据
                for key, selector in item_selectors.items():
                    try:
                        text = await self.appium_handler.get_text(By.XPATH, selector)
                        item_data[key] = text
                    except Exception as e:
                        if self.logger:
                            self.logger.warning(f"提取项目 {i} 的 {key} 失败: {e}")
                        item_data[key] = ""
                
                results.append(item_data)
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"提取列表数据失败: {e}")
        
        return results
    
    async def scroll_and_collect(self, collect_function, max_scrolls: int = 10) -> List[Any]:
        """滚动并收集数据"""
        all_results = []
        scroll_count = 0
        
        while scroll_count < max_scrolls:
            try:
                # 收集当前页面数据
                current_results = await collect_function()
                
                if current_results:
                    all_results.extend(current_results)
                    if self.logger:
                        self.logger.info(f"滚动 {scroll_count + 1}: 收集到 {len(current_results)} 条数据")
                
                # 滚动页面
                if not await self.appium_handler.scroll_down():
                    break
                
                # 等待内容加载
                await asyncio.sleep(2)
                scroll_count += 1
                
            except Exception as e:
                if self.logger:
                    self.logger.error(f"滚动收集数据失败: {e}")
                break
        
        if self.logger:
            self.logger.info(f"总共收集到 {len(all_results)} 条数据")
        
        return all_results
    
    async def cleanup(self):
        """清理资源"""
        try:
            if self.logger:
                self.logger.info("正在清理移动端资源...")
            
            # 关闭Appium驱动
            await self.appium_handler.close()
            
            # 停止模拟器（可选）
            # await self.emulator.stop_emulator()
            
            if self.logger:
                self.logger.info("移动端资源清理完成")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"清理资源失败: {e}")


# 移动端爬虫工厂
class MobileSpiderFactory:
    """移动端爬虫工厂"""
    
    @staticmethod
    def create_app_spider(target: str, app_package: str, app_activity: str = None, 
                         config_path: str = 'config.json', logger=None) -> MobileSpider:
        """创建应用爬虫"""
        spider = MobileSpider(target, config_path, workers=1, logger=logger)
        spider.mobile_config.app_package = app_package
        spider.mobile_config.app_activity = app_activity
        return spider
    
    @staticmethod
    def create_browser_spider(target: str, config_path: str = 'config.json', 
                            logger=None) -> MobileSpider:
        """创建移动浏览器爬虫"""
        spider = MobileSpider(target, config_path, workers=1, logger=logger)
        spider.mobile_config.app_package = "com.android.chrome"
        spider.mobile_config.app_activity = "com.google.android.apps.chrome.Main"
        return spider