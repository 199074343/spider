#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
工具模块单元测试
"""

import asyncio
import json
import tempfile
import os
from pathlib import Path

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_framework import TestCase, create_test_suite
from tests.mocks import MockLogger, MockHttpSession, MockHttpResponse, TestDataGenerator
from utils.data_processor import DataProcessor
from utils.storage import Storage
from utils.request_handler import RequestHandler


class TestDataProcessor(TestCase):
    """测试数据处理器"""
    
    async def setup(self):
        """测试前置操作"""
        self.logger = MockLogger()
        self.processor = DataProcessor(logger=self.logger)
        self.test_html = TestDataGenerator.generate_html_content(
            "Test Title", "Test Content with special chars !@#$%"
        )
    
    def test_parse_html(self):
        """测试HTML解析"""
        soup = self.processor.parse_html(self.test_html)
        self.assert_is_not_none(soup, "HTML解析应该成功")
        
        # 测试标题提取
        title = soup.find('title')
        self.assert_is_not_none(title)
        self.assert_equal(title.text, "Test Title")
    
    def test_parse_html_invalid(self):
        """测试无效HTML解析"""
        soup = self.processor.parse_html("invalid html <><")
        # BeautifulSoup应该能处理无效HTML
        self.assert_is_not_none(soup)
    
    def test_extract_text(self):
        """测试文本提取"""
        soup = self.processor.parse_html(self.test_html)
        
        # 提取标题
        title = self.processor.extract_text(soup, '#title')
        self.assert_equal(title, "Test Title")
        
        # 提取内容
        content = self.processor.extract_text(soup, '.content p')
        self.assert_in("Test Content", content)
        
        # 提取不存在的元素
        nonexistent = self.processor.extract_text(soup, '#nonexistent')
        self.assert_equal(nonexistent, "")
    
    def test_extract_links(self):
        """测试链接提取"""
        soup = self.processor.parse_html(self.test_html)
        links = self.processor.extract_links(soup, "https://test.com")
        
        self.assert_equal(len(links), 2)
        self.assert_in("https://test.com/link1", links)
        self.assert_in("https://test.com/link2", links)
    
    def test_extract_images(self):
        """测试图片提取"""
        soup = self.processor.parse_html(self.test_html)
        images = self.processor.extract_images(soup, "https://test.com")
        
        self.assert_equal(len(images), 2)
        self.assert_in("https://test.com/image1.jpg", images)
        self.assert_in("https://test.com/image2.jpg", images)
    
    def test_clean_text(self):
        """测试文本清理"""
        dirty_text = "  Hello   World!  \n\t  @#$%  "
        clean_text = self.processor.clean_text(dirty_text)
        
        self.assert_equal(clean_text, "Hello World")
        
        # 测试空文本
        empty_clean = self.processor.clean_text("")
        self.assert_equal(empty_clean, "")
        
        # 测试None
        none_clean = self.processor.clean_text(None)
        self.assert_equal(none_clean, "")
    
    def test_extract_by_rules(self):
        """测试规则提取"""
        soup = self.processor.parse_html(self.test_html)
        
        rules = {
            'title': '#title',
            'content': '.content p',
            'items': '.item',
            'nonexistent': '#nonexistent'
        }
        
        result = self.processor.extract_by_rules(soup, rules)
        
        self.assert_equal(result['title'], "Test Title")
        self.assert_in("Test Content", result['content'])
        self.assert_equal(result['nonexistent'], "")


class TestStorage(TestCase):
    """测试存储器"""
    
    async def setup(self):
        """测试前置操作"""
        self.logger = MockLogger()
        self.storage = Storage(logger=self.logger)
        self.test_data = TestDataGenerator.generate_json_data(3)
        self.test_path = "test_storage_data"
        
    async def teardown(self):
        """测试后置操作"""
        # 清理测试文件
        test_path = Path(self.test_path)
        if test_path.exists():
            import shutil
            shutil.rmtree(test_path)
    
    async def test_save_json(self):
        """测试JSON保存"""
        await self.storage.save(
            data=self.test_data,
            format='json',
            path=self.test_path,
            filename='test_json'
        )
        
        # 验证文件是否创建
        json_file = Path(self.test_path) / 'test_json.json'
        self.assert_true(json_file.exists(), "JSON文件应该被创建")
        
        # 验证文件内容
        with open(json_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        self.assert_equal(len(saved_data), 3)
        self.assert_equal(saved_data[0]['title'], 'Test Item 1')
    
    async def test_save_csv(self):
        """测试CSV保存"""
        await self.storage.save(
            data=self.test_data,
            format='csv',
            path=self.test_path,
            filename='test_csv'
        )
        
        # 验证文件是否创建
        csv_file = Path(self.test_path) / 'test_csv.csv'
        self.assert_true(csv_file.exists(), "CSV文件应该被创建")
        
        # 验证文件内容
        import pandas as pd
        df = pd.read_csv(csv_file)
        self.assert_equal(len(df), 3)
        self.assert_in('title', df.columns)
    
    async def test_save_excel(self):
        """测试Excel保存"""
        await self.storage.save(
            data=self.test_data,
            format='excel',
            path=self.test_path,
            filename='test_excel'
        )
        
        # 验证文件是否创建
        excel_file = Path(self.test_path) / 'test_excel.xlsx'
        self.assert_true(excel_file.exists(), "Excel文件应该被创建")
        
        # 验证文件内容
        import pandas as pd
        df = pd.read_excel(excel_file)
        self.assert_equal(len(df), 3)
        self.assert_in('title', df.columns)
    
    async def test_save_empty_data(self):
        """测试保存空数据"""
        await self.storage.save(
            data=[],
            format='json',
            path=self.test_path,
            filename='test_empty'
        )
        
        # 对于空数据，某些格式可能不创建文件
        # 这里主要测试不会抛出异常
        self.assert_true(True, "保存空数据应该不抛出异常")
    
    async def test_load_json(self):
        """测试JSON加载"""
        # 先保存数据
        await self.storage.save(
            data=self.test_data,
            format='json',
            path=self.test_path,
            filename='test_load'
        )
        
        # 加载数据
        json_file = Path(self.test_path) / 'test_load.json'
        loaded_data = await self.storage.load_json(str(json_file))
        
        self.assert_equal(len(loaded_data), 3)
        self.assert_equal(loaded_data[0]['title'], 'Test Item 1')
    
    async def test_load_json_nonexistent(self):
        """测试加载不存在的JSON文件"""
        loaded_data = await self.storage.load_json("nonexistent.json")
        self.assert_equal(loaded_data, [])
        
        # 检查错误日志
        error_logs = self.logger.get_logs('ERROR')
        self.assert_true(len(error_logs) > 0, "应该记录加载失败的错误")


class TestRequestHandler(TestCase):
    """测试请求处理器"""
    
    async def setup(self):
        """测试前置操作"""
        self.logger = MockLogger()
        self.handler = RequestHandler(logger=self.logger)
        
    async def test_fetch_success(self):
        """测试成功请求"""
        mock_session = MockHttpSession()
        mock_session.set_response(
            "https://test.com",
            MockHttpResponse("Success response", 200)
        )
        
        response = await self.handler.fetch(mock_session, "https://test.com")
        
        self.assert_is_not_none(response)
        self.assert_equal(response.status, 200)
        
        content = await response.text()
        self.assert_equal(content, "Success response")
    
    async def test_fetch_retry_on_server_error(self):
        """测试服务器错误时的重试"""
        mock_session = MockHttpSession()
        
        # 设置第一次请求返回503，第二次返回200
        call_count = 0
        original_request = mock_session.request
        
        async def mock_request_with_retry(method, url, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return MockHttpResponse("Server Error", 503)
            else:
                return MockHttpResponse("Success", 200)
        
        mock_session.request = mock_request_with_retry
        
        response = await self.handler.fetch(mock_session, "https://test.com", max_retries=3)
        
        self.assert_is_not_none(response)
        self.assert_equal(response.status, 200)
        self.assert_equal(call_count, 2, "应该重试一次")
    
    async def test_fetch_max_retries_exceeded(self):
        """测试超过最大重试次数"""
        mock_session = MockHttpSession()
        mock_session.set_default_response(MockHttpResponse("Server Error", 503))
        
        response = await self.handler.fetch(mock_session, "https://test.com", max_retries=2)
        
        self.assert_is_none(response, "超过重试次数应该返回None")
        
        # 检查请求次数
        requests = mock_session.get_requests()
        self.assert_equal(len(requests), 2, "应该尝试2次请求")


# 创建工具模块测试套件
utils_test_suite = create_test_suite("Utils Module Tests")
utils_test_suite.add_test_case(TestDataProcessor())
utils_test_suite.add_test_case(TestStorage())
utils_test_suite.add_test_case(TestRequestHandler())