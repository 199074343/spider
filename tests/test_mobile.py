#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
移动端模块单元测试
"""

import asyncio
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_framework import TestCase, create_test_suite
from tests.mocks import MockLogger, MockAndroidEmulator, MockAppiumDriver, TestDataGenerator
from utils.android_emulator import AndroidEmulator
from utils.appium_handler import AppiumHandler
from mobile_spider import MobileSpider, MobileSpiderConfig


class TestAndroidEmulator(TestCase):
    """测试Android模拟器"""
    
    async def setup(self):
        """测试前置操作"""
        self.logger = MockLogger()
        self.emulator = MockAndroidEmulator(logger=self.logger)
    
    async def test_start_emulator(self):
        """测试启动模拟器"""
        result = await self.emulator.start_emulator("test_avd", 5554)
        self.assert_true(result, "模拟器应该启动成功")
        self.assert_true(self.emulator.is_running, "模拟器状态应该为运行中")
    
    async def test_connect_device(self):
        """测试连接设备"""
        result = await self.emulator.connect_device()
        self.assert_true(result, "设备连接应该成功")
        self.assert_true(self.emulator.device_connected, "设备状态应该为已连接")
    
    async def test_install_app(self):
        """测试安装应用"""
        result = await self.emulator.install_app("/path/to/test.apk")
        self.assert_true(result, "应用安装应该成功")
        self.assert_in("/path/to/test.apk", self.emulator.installed_apps)
    
    async def test_get_device_info(self):
        """测试获取设备信息"""
        device_info = await self.emulator.get_device_info()
        
        self.assert_is_not_none(device_info)
        self.assert_in('model', device_info)
        self.assert_in('android_version', device_info)
        self.assert_equal(device_info['model'], 'Mock Device')
    
    async def test_take_screenshot(self):
        """测试截图功能"""
        screenshot_path = "test_screenshot.png"
        
        try:
            result = await self.emulator.take_screenshot(screenshot_path)
            self.assert_true(result, "截图应该成功")
            self.assert_true(Path(screenshot_path).exists(), "截图文件应该存在")
        finally:
            # 清理截图文件
            if Path(screenshot_path).exists():
                os.remove(screenshot_path)
    
    async def test_stop_emulator(self):
        """测试停止模拟器"""
        await self.emulator.start_emulator("test_avd")
        result = await self.emulator.stop_emulator()
        
        self.assert_true(result, "模拟器停止应该成功")
        self.assert_false(self.emulator.is_running, "模拟器状态应该为停止")


class TestAppiumHandler(TestCase):
    """测试Appium处理器"""
    
    async def setup(self):
        """测试前置操作"""
        self.logger = MockLogger()
        self.handler = AppiumHandler(logger=self.logger)
        self.mock_driver = MockAppiumDriver()
        self.handler.driver = self.mock_driver
    
    async def test_find_element(self):
        """测试查找元素"""
        # 设置Mock元素
        mock_element = Mock()
        mock_element.text = "Test Element"
        
        with patch('selenium.webdriver.support.ui.WebDriverWait') as mock_wait:
            mock_wait.return_value.until.return_value = mock_element
            
            element = await self.handler.find_element("id", "test_id")
            self.assert_is_not_none(element)
    
    async def test_click_element(self):
        """测试点击元素"""
        mock_element = Mock()
        
        with patch.object(self.handler, 'find_element', return_value=mock_element):
            result = await self.handler.click_element("id", "test_button")
            self.assert_true(result, "点击应该成功")
            mock_element.click.assert_called_once()
    
    async def test_input_text(self):
        """测试文本输入"""
        mock_element = Mock()
        
        with patch.object(self.handler, 'find_element', return_value=mock_element):
            result = await self.handler.input_text("id", "test_input", "test text")
            self.assert_true(result, "文本输入应该成功")
            mock_element.clear.assert_called_once()
            mock_element.send_keys.assert_called_once_with("test text")
    
    async def test_get_text(self):
        """测试获取文本"""
        mock_element = Mock()
        mock_element.text = "Element Text"
        
        with patch.object(self.handler, 'find_element', return_value=mock_element):
            text = await self.handler.get_text("id", "test_element")
            self.assert_equal(text, "Element Text")
    
    async def test_scroll_down(self):
        """测试向下滚动"""
        result = await self.handler.scroll_down()
        self.assert_true(result, "滚动应该成功")
        
        # 验证滚动命令被执行
        commands = self.mock_driver.commands_executed
        swipe_commands = [cmd for cmd in commands if cmd.get('command') == 'swipe']
        self.assert_true(len(swipe_commands) > 0, "应该执行滚动命令")
    
    async def test_take_screenshot(self):
        """测试移动端截图"""
        screenshot_path = "mobile_test_screenshot.png"
        
        try:
            result = await self.handler.take_screenshot(screenshot_path)
            self.assert_true(result, "移动端截图应该成功")
            self.assert_in(screenshot_path, self.mock_driver.screenshots_taken)
        finally:
            # 清理截图文件
            if Path(screenshot_path).exists():
                os.remove(screenshot_path)


class TestMobileSpider(TestCase):
    """测试移动端爬虫"""
    
    async def setup(self):
        """测试前置操作"""
        self.logger = MockLogger()
        self.test_config = {
            "mobile_test": {
                "target": "mobile_test",
                "base_url": "https://m.test.com",
                "headers": {},
                "delay": 0.1,
                "timeout": 30,
                "max_retries": 2,
                "output_format": "json",
                "output_path": "mobile_test_data",
                "avd_name": "test_avd",
                "emulator_port": 5554,
                "appium_server_url": "http://localhost:4723",
                "platform_name": "Android",
                "platform_version": "11.0",
                "device_name": "emulator-5554",
                "automation_name": "UiAutomator2",
                "app_package": "com.test.app",
                "app_activity": "com.test.app.MainActivity",
                "no_reset": True,
                "new_command_timeout": 300
            }
        }
        
        self.config_file = TestDataGenerator.create_temp_config(self.test_config)
        
    async def teardown(self):
        """测试后置操作"""
        if hasattr(self, 'config_file') and os.path.exists(self.config_file):
            os.remove(self.config_file)
        
        # 清理测试数据
        test_data_path = Path("mobile_test_data")
        if test_data_path.exists():
            import shutil
            shutil.rmtree(test_data_path)
    
    def test_mobile_spider_config_creation(self):
        """测试移动端配置创建"""
        config = MobileSpiderConfig(
            target="mobile_test",
            base_url="https://m.test.com",
            headers={},
            avd_name="test_avd",
            app_package="com.test.app"
        )
        
        self.assert_equal(config.target, "mobile_test")
        self.assert_equal(config.avd_name, "test_avd")
        self.assert_equal(config.app_package, "com.test.app")
        self.assert_equal(config.platform_name, "Android")
        self.assert_equal(config.automation_name, "UiAutomator2")
    
    async def test_mobile_spider_initialization(self):
        """测试移动端爬虫初始化"""
        spider = MobileSpider(
            target="mobile_test",
            config_path=self.config_file,
            workers=1,
            logger=self.logger
        )
        
        self.assert_equal(spider.target, "mobile_test")
        self.assert_equal(spider.workers, 1)
        self.assert_is_not_none(spider.emulator)
        self.assert_is_not_none(spider.appium_handler)
        self.assert_is_not_none(spider.mobile_config)
    
    async def test_mobile_config_loading(self):
        """测试移动端配置加载"""
        spider = MobileSpider(
            target="mobile_test",
            config_path=self.config_file,
            logger=self.logger
        )
        
        config = spider.mobile_config
        self.assert_equal(config.avd_name, "test_avd")
        self.assert_equal(config.app_package, "com.test.app")
        self.assert_equal(config.platform_name, "Android")
        self.assert_equal(config.emulator_port, 5554)
    
    async def test_setup_mobile_environment(self):
        """测试移动端环境设置"""
        spider = MobileSpider(
            target="mobile_test",
            config_path=self.config_file,
            logger=self.logger
        )
        
        # 使用Mock对象
        spider.emulator = MockAndroidEmulator(self.logger)
        
        mock_appium_handler = Mock()
        mock_appium_handler.setup_driver = AsyncMock(return_value=True)
        spider.appium_handler = mock_appium_handler
        
        result = await spider.setup_mobile_environment()
        self.assert_true(result, "移动端环境设置应该成功")
        
        # 验证模拟器启动
        self.assert_true(spider.emulator.is_running)
        self.assert_true(spider.emulator.device_connected)
        
        # 验证Appium设置被调用
        mock_appium_handler.setup_driver.assert_called_once()


class TestMobileSpiderIntegration(TestCase):
    """测试移动端爬虫集成功能"""
    
    async def setup(self):
        """测试前置操作"""
        self.logger = MockLogger()
        self.test_config = {
            "mobile_integration": {
                "target": "mobile_integration",
                "base_url": "https://m.test.com",
                "headers": {},
                "delay": 0.1,
                "timeout": 30,
                "output_format": "json",
                "output_path": "mobile_integration_data",
                "avd_name": "test_avd",
                "app_package": "com.test.app"
            }
        }
        
        self.config_file = TestDataGenerator.create_temp_config(self.test_config)
        
    async def teardown(self):
        """测试后置操作"""
        if hasattr(self, 'config_file') and os.path.exists(self.config_file):
            os.remove(self.config_file)
        
        # 清理测试数据
        test_data_path = Path("mobile_integration_data")
        if test_data_path.exists():
            import shutil
            shutil.rmtree(test_data_path)
        
        # 清理截图目录
        screenshots_path = Path("screenshots")
        if screenshots_path.exists():
            import shutil
            shutil.rmtree(screenshots_path)
    
    async def test_mobile_spider_full_workflow(self):
        """测试移动端爬虫完整工作流程"""
        
        class TestMobileSpiderImpl(MobileSpider):
            async def execute_mobile_tasks(self):
                return [
                    {
                        'page_type': 'test',
                        'title': 'Test Mobile Page',
                        'content': 'Test mobile content',
                        'timestamp': 1234567890
                    }
                ]
        
        spider = TestMobileSpiderImpl(
            target="mobile_integration",
            config_path=self.config_file,
            workers=1,
            logger=self.logger
        )
        
        # 使用Mock对象
        spider.emulator = MockAndroidEmulator(self.logger)
        
        mock_appium_handler = Mock()
        mock_appium_handler.setup_driver = AsyncMock(return_value=True)
        mock_appium_handler.close = AsyncMock()
        spider.appium_handler = mock_appium_handler
        
        # Mock存储器
        from mocks import MockStorage
        mock_storage = MockStorage(self.logger)
        spider.storage = mock_storage
        
        # 运行爬虫
        await spider.run()
        
        # 验证结果
        saved_data = mock_storage.get_saved_data()
        self.assert_equal(len(saved_data), 1)
        self.assert_equal(saved_data[0]['title'], 'Test Mobile Page')
        
        # 验证环境设置被调用
        self.assert_true(spider.emulator.is_running)
        mock_appium_handler.setup_driver.assert_called_once()
        mock_appium_handler.close.assert_called_once()
    
    async def test_navigate_to_url(self):
        """测试URL导航"""
        spider = MobileSpider(
            target="mobile_integration",
            config_path=self.config_file,
            logger=self.logger
        )
        
        mock_driver = MockAppiumDriver()
        spider.appium_handler.driver = mock_driver
        
        result = await spider.navigate_to_url("https://m.test.com")
        self.assert_true(result, "URL导航应该成功")
        
        # 验证导航命令被执行
        commands = mock_driver.commands_executed
        get_commands = [cmd for cmd in commands if cmd.get('command') == 'get']
        self.assert_equal(len(get_commands), 1)
        self.assert_equal(get_commands[0]['url'], "https://m.test.com")
    
    async def test_extract_list_data(self):
        """测试列表数据提取"""
        spider = MobileSpider(
            target="mobile_integration",
            config_path=self.config_file,
            logger=self.logger
        )
        
        # Mock Appium handler
        mock_handler = Mock()
        mock_elements = [
            Mock(text="Item 1"),
            Mock(text="Item 2"),
            Mock(text="Item 3")
        ]
        mock_handler.find_elements = AsyncMock(return_value=mock_elements)
        mock_handler.get_text = AsyncMock(side_effect=["Title 1", "Title 2", "Title 3"])
        spider.appium_handler = mock_handler
        
        item_selectors = {
            'title': ".//android.widget.TextView[@resource-id='title']"
        }
        
        results = await spider.extract_list_data("//android.widget.ListView", item_selectors)
        
        self.assert_equal(len(results), 3)
        self.assert_equal(results[0]['index'], 0)
        # Note: 由于mock的限制，这里主要测试方法调用和基本结构
    
    async def test_scroll_and_collect(self):
        """测试滚动收集数据"""
        spider = MobileSpider(
            target="mobile_integration",
            config_path=self.config_file,
            logger=self.logger
        )
        
        # Mock Appium handler
        mock_handler = Mock()
        mock_handler.scroll_down = AsyncMock(side_effect=[True, True, False])  # 滚动两次后停止
        spider.appium_handler = mock_handler
        
        call_count = 0
        async def mock_collect_function():
            nonlocal call_count
            call_count += 1
            return [{'data': f'page_{call_count}'}]
        
        results = await spider.scroll_and_collect(mock_collect_function, max_scrolls=5)
        
        # 验证收集到的数据
        self.assert_true(len(results) >= 2, "应该收集到至少2页数据")
        
        # 验证滚动被调用
        self.assert_equal(mock_handler.scroll_down.call_count, 3)


# 创建移动端测试套件
mobile_test_suite = create_test_suite("Mobile Module Tests")
mobile_test_suite.add_test_case(TestAndroidEmulator())
mobile_test_suite.add_test_case(TestAppiumHandler())
mobile_test_suite.add_test_case(TestMobileSpider())
mobile_test_suite.add_test_case(TestMobileSpiderIntegration())