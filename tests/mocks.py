#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试用Mock对象和工具
"""

import asyncio
import json
import tempfile
import os
import time
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, AsyncMock
from pathlib import Path


class MockLogger:
    """模拟日志器"""
    
    def __init__(self):
        self.logs = []
        
    def info(self, message: str):
        self.logs.append(('INFO', message))
        
    def debug(self, message: str):
        self.logs.append(('DEBUG', message))
        
    def warning(self, message: str):
        self.logs.append(('WARNING', message))
        
    def error(self, message: str):
        self.logs.append(('ERROR', message))
        
    def get_logs(self, level: str = None) -> List[tuple]:
        """获取日志记录"""
        if level:
            return [log for log in self.logs if log[0] == level.upper()]
        return self.logs
    
    def clear_logs(self):
        """清空日志"""
        self.logs.clear()


class MockHttpResponse:
    """模拟HTTP响应"""
    
    def __init__(self, text: str = "", status: int = 200, headers: Dict = None, json_data: Dict = None):
        self._text = text
        self.status = status
        self.headers = headers or {}
        self._json_data = json_data
        
    async def text(self):
        """返回文本内容"""
        return self._text
        
    async def json(self):
        """返回JSON内容"""
        if self._json_data:
            return self._json_data
        return json.loads(self._text) if self._text else {}
    
    async def read(self):
        """返回字节内容"""
        return self._text.encode('utf-8')


class MockHttpContextManager:
    """Mock HTTP上下文管理器"""
    
    def __init__(self, response):
        self.response = response
    
    async def __aenter__(self):
        return self.response
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class MockHttpSession:
    """模拟HTTP会话"""
    
    def __init__(self):
        self.responses = {}
        self.requests_made = []
        self.default_response = MockHttpResponse("Default response", 200)
        
    def set_response(self, url: str, response: MockHttpResponse):
        """设置特定URL的响应"""
        self.responses[url] = response
        
    def set_default_response(self, response: MockHttpResponse):
        """设置默认响应"""
        self.default_response = response
    
    def request(self, method: str, url: str, **kwargs):
        """模拟请求 - 返回上下文管理器"""
        request_info = {
            'method': method,
            'url': url,
            'kwargs': kwargs
        }
        self.requests_made.append(request_info)
        
        # 返回预设的响应
        if url in self.responses:
            response = self.responses[url]
        else:
            response = self.default_response
            
        return MockHttpContextManager(response)
    
    async def get(self, url: str, **kwargs):
        """直接返回响应（非上下文管理器版本）"""
        request_info = {
            'method': 'GET',
            'url': url,
            'kwargs': kwargs
        }
        self.requests_made.append(request_info)
        
        if url in self.responses:
            return self.responses[url]
        return self.default_response
    
    async def post(self, url: str, **kwargs):
        """直接返回响应（非上下文管理器版本）"""
        request_info = {
            'method': 'POST',
            'url': url,
            'kwargs': kwargs
        }
        self.requests_made.append(request_info)
        
        if url in self.responses:
            return self.responses[url]
        return self.default_response
    
    def get_requests(self) -> List[Dict]:
        """获取所有请求记录"""
        return self.requests_made
    
    def clear_requests(self):
        """清空请求记录"""
        self.requests_made.clear()


class MockAppiumDriver:
    """模拟Appium驱动"""
    
    def __init__(self):
        self.elements = {}
        self.page_source = "<html><body>Mock page</body></html>"
        self.window_size = {'width': 1080, 'height': 1920}
        self.screenshots_taken = []
        self.commands_executed = []
        
    def find_element(self, by: str, value: str):
        """查找元素"""
        element_key = f"{by}:{value}"
        if element_key in self.elements:
            return self.elements[element_key]
        
        # 返回默认Mock元素
        mock_element = MockAppiumElement(f"Mock element for {value}")
        return mock_element
    
    def find_elements(self, by: str, value: str):
        """查找多个元素"""
        element_key = f"{by}:{value}"
        if element_key in self.elements:
            elements = self.elements[element_key]
            return elements if isinstance(elements, list) else [elements]
        
        # 返回默认Mock元素列表
        return [MockAppiumElement(f"Mock element {i} for {value}") for i in range(3)]
    
    def get_window_size(self):
        """获取窗口大小"""
        return self.window_size
    
    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int):
        """滑动操作"""
        self.commands_executed.append({
            'command': 'swipe',
            'start_x': start_x,
            'start_y': start_y,
            'end_x': end_x,
            'end_y': end_y,
            'duration': duration
        })
    
    def save_screenshot(self, filename: str):
        """保存截图"""
        self.screenshots_taken.append(filename)
        # 创建一个空的截图文件
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        with open(filename, 'w') as f:
            f.write("Mock screenshot")
    
    def get(self, url: str):
        """导航到URL"""
        self.commands_executed.append({
            'command': 'get',
            'url': url
        })
    
    def quit(self):
        """退出驱动"""
        self.commands_executed.append({'command': 'quit'})
    
    def set_mock_element(self, by: str, value: str, element):
        """设置Mock元素"""
        self.elements[f"{by}:{value}"] = element
    
    def set_page_source(self, source: str):
        """设置页面源码"""
        self.page_source = source


class MockAppiumElement:
    """模拟Appium元素"""
    
    def __init__(self, text: str = "", attributes: Dict = None):
        self.text = text
        self.attributes = attributes or {}
        self.clicked = False
        self.input_text = ""
        
    def click(self):
        """点击元素"""
        self.clicked = True
    
    def clear(self):
        """清空元素"""
        self.input_text = ""
    
    def send_keys(self, text: str):
        """输入文本"""
        self.input_text += text
    
    def get_attribute(self, name: str):
        """获取属性"""
        return self.attributes.get(name, "")
    
    def find_element(self, by: str, value: str):
        """在元素内查找子元素"""
        return MockAppiumElement(f"Child element: {value}")
    
    def find_elements(self, by: str, value: str):
        """在元素内查找多个子元素"""
        return [MockAppiumElement(f"Child element {i}: {value}") for i in range(2)]


class MockAndroidEmulator:
    """模拟Android模拟器"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.is_running = False
        self.device_connected = False
        self.installed_apps = []
        self.device_info = {
            'model': 'Mock Device',
            'android_version': '11.0',
            'manufacturer': 'Mock',
            'sdk_version': '30'
        }
        
    async def start_emulator(self, avd_name: str, port: int = 5554) -> bool:
        """模拟启动模拟器"""
        await asyncio.sleep(0.1)  # 模拟启动时间
        self.is_running = True
        return True
    
    async def connect_device(self) -> bool:
        """模拟连接设备"""
        await asyncio.sleep(0.1)
        self.device_connected = True
        return True
    
    async def install_app(self, apk_path: str) -> bool:
        """模拟安装应用"""
        await asyncio.sleep(0.1)
        self.installed_apps.append(apk_path)
        return True
    
    async def get_device_info(self) -> Dict[str, str]:
        """模拟获取设备信息"""
        return self.device_info
    
    async def take_screenshot(self, save_path: str = "screenshot.png") -> bool:
        """模拟截图"""
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, 'w') as f:
            f.write("Mock screenshot")
        return True
    
    async def stop_emulator(self) -> bool:
        """模拟停止模拟器"""
        self.is_running = False
        self.device_connected = False
        return True


class TestDataGenerator:
    """测试数据生成器"""
    
    @staticmethod
    def generate_html_content(title: str = "Test Title", content: str = "Test Content") -> str:
        """生成HTML测试内容"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
        </head>
        <body>
            <h1 id="title">{title}</h1>
            <div class="content">
                <p>{content}</p>
                <a href="/link1">Link 1</a>
                <a href="/link2">Link 2</a>
                <img src="/image1.jpg" alt="Image 1">
                <img src="/image2.jpg" alt="Image 2">
            </div>
            <ul class="list">
                <li class="item">Item 1</li>
                <li class="item">Item 2</li>
                <li class="item">Item 3</li>
            </ul>
        </body>
        </html>
        """
    
    @staticmethod
    def generate_json_data(count: int = 3) -> List[Dict[str, Any]]:
        """生成JSON测试数据"""
        return [
            {
                'id': i,
                'title': f'Test Item {i}',
                'description': f'Description for item {i}',
                'url': f'https://example.com/item/{i}',
                'timestamp': time.time()
            }
            for i in range(1, count + 1)
        ]
    
    @staticmethod
    def create_temp_config(config_data: Dict[str, Any]) -> str:
        """创建临时配置文件"""
        fd, path = tempfile.mkstemp(suffix='.json')
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
        except Exception:
            os.close(fd)
            raise
        
        return path


class MockStorage:
    """模拟存储器"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.saved_data = []
        self.save_calls = []
        
    async def save(self, data: List[Dict[str, Any]], format: str = 'json', 
                  path: str = 'data', filename: str = 'results'):
        """模拟保存数据"""
        save_info = {
            'data': data,
            'format': format,
            'path': path,
            'filename': filename,
            'timestamp': time.time()
        }
        
        self.save_calls.append(save_info)
        self.saved_data.extend(data)
        
        # 实际创建文件（用于测试）
        Path(path).mkdir(parents=True, exist_ok=True)
        filepath = Path(path) / f"{filename}.{format}"
        
        if format == 'json':
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_saved_data(self) -> List[Dict[str, Any]]:
        """获取保存的数据"""
        return self.saved_data
    
    def get_save_calls(self) -> List[Dict[str, Any]]:
        """获取保存调用记录"""
        return self.save_calls
    
    def clear(self):
        """清空记录"""
        self.saved_data.clear()
        self.save_calls.clear()