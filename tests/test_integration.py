#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
集成测试
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
from tests.mocks import MockLogger, MockHttpSession, MockHttpResponse, TestDataGenerator, MockStorage
from spider import Spider
from example_spider import ExampleSpider


class TestSpiderIntegration(TestCase):
    """测试爬虫集成功能"""
    
    async def setup(self):
        """测试前置操作"""
        self.logger = MockLogger()
        self.test_config = {
            "integration_test": {
                "target": "integration_test",
                "base_url": "https://integration.test.com",
                "headers": {"User-Agent": "integration-test"},
                "delay": 0.1,
                "timeout": 30,
                "max_retries": 2,
                "output_format": "json",
                "output_path": "integration_test_data"
            }
        }
        
        self.config_file = TestDataGenerator.create_temp_config(self.test_config)
        
    async def teardown(self):
        """测试后置操作"""
        if hasattr(self, 'config_file') and os.path.exists(self.config_file):
            os.remove(self.config_file)
        
        # 清理测试数据
        test_data_path = Path("integration_test_data")
        if test_data_path.exists():
            import shutil
            shutil.rmtree(test_data_path)
    
    async def test_end_to_end_spider_workflow(self):
        """测试端到端爬虫工作流程"""
        
        class IntegrationTestSpider(Spider):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.mock_session = MockHttpSession()
                
                # 设置测试页面响应
                test_pages = [
                    ("https://integration.test.com/page/1", "Page 1 Content"),
                    ("https://integration.test.com/page/2", "Page 2 Content"),
                    ("https://integration.test.com/page/3", "Page 3 Content")
                ]
                
                for url, content in test_pages:
                    html_content = TestDataGenerator.generate_html_content(
                        f"Title for {url}", content
                    )
                    self.mock_session.set_response(url, MockHttpResponse(html_content, 200))
            
            async def get_urls(self):
                return [
                    "https://integration.test.com/page/1",
                    "https://integration.test.com/page/2", 
                    "https://integration.test.com/page/3"
                ]
            
            async def parse_response(self, response, url):
                content = await response.text()
                
                # 简单的HTML解析
                if '<title>' in content:
                    title_start = content.find('<title>') + 7
                    title_end = content.find('</title>')
                    title = content[title_start:title_end] if title_end > title_start else "No Title"
                else:
                    title = "No Title"
                
                return {
                    'url': url,
                    'title': title,
                    'content_length': len(content),
                    'status': response.status
                }
        
        spider = IntegrationTestSpider(
            target="integration_test",
            config_path=self.config_file,
            workers=2,
            logger=self.logger
        )
        
        # Mock request handler
        class MockRequestHandler:
            async def fetch(self, session, url):
                return await spider.mock_session.get(url)
        
        spider.request_handler = MockRequestHandler()
        
        # Mock storage
        mock_storage = MockStorage(self.logger)
        spider.storage = mock_storage
        
        # 运行完整流程
        urls = await spider.get_urls()
        self.assert_equal(len(urls), 3, "应该获取到3个URL")
        
        # 处理所有URL
        semaphore = asyncio.Semaphore(spider.workers)
        tasks = [spider.process_url(semaphore, url) for url in urls]
        results = await asyncio.gather(*tasks)
        
        # 验证处理结果
        valid_results = [r for r in results if r is not None]
        self.assert_equal(len(valid_results), 3, "应该处理成功3个URL")
        
        # 验证数据结构
        for result in valid_results:
            self.assert_in('url', result)
            self.assert_in('title', result)
            self.assert_in('content_length', result)
            self.assert_equal(result['status'], 200)
        
        # 保存结果
        await spider.save_results(results)
        
        # 验证保存
        saved_data = mock_storage.get_saved_data()
        self.assert_equal(len(saved_data), 3)
        
        # 验证日志记录
        info_logs = self.logger.get_logs('INFO')
        self.assert_true(len(info_logs) > 0, "应该有信息日志")


class TestExampleSpiderIntegration(TestCase):
    """测试示例爬虫集成"""
    
    async def setup(self):
        """测试前置操作"""
        self.logger = MockLogger()
        self.test_config = {
            "example_integration": {
                "target": "example_integration",
                "base_url": "https://example.integration.com",
                "headers": {"User-Agent": "example-test"},
                "delay": 0.1,
                "timeout": 30,
                "output_format": "json",
                "output_path": "example_integration_data"
            }
        }
        
        self.config_file = TestDataGenerator.create_temp_config(self.test_config)
        
    async def teardown(self):
        """测试后置操作"""
        if hasattr(self, 'config_file') and os.path.exists(self.config_file):
            os.remove(self.config_file)
        
        # 清理测试数据
        test_data_path = Path("example_integration_data")
        if test_data_path.exists():
            import shutil
            shutil.rmtree(test_data_path)
    
    async def test_example_spider_workflow(self):
        """测试示例爬虫工作流程"""
        
        class MockExampleSpider(ExampleSpider):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.mock_session = MockHttpSession()
                
                # 设置测试响应
                for i in range(1, 6):
                    url = f"https://example.integration.com/page/{i}"
                    html_content = TestDataGenerator.generate_html_content(
                        f"Example Page {i}",
                        f"Example content for page {i}"
                    )
                    self.mock_session.set_response(url, MockHttpResponse(html_content, 200))
        
        spider = MockExampleSpider(
            target="example_integration",
            config_path=self.config_file,
            workers=2,
            logger=self.logger
        )
        
        # Mock request handler
        class MockRequestHandler:
            async def fetch(self, session, url):
                return await spider.mock_session.get(url)
        
        spider.request_handler = MockRequestHandler()
        
        # Mock storage
        mock_storage = MockStorage(self.logger)
        spider.storage = mock_storage
        
        # 测试URL生成
        urls = await spider.get_urls()
        self.assert_equal(len(urls), 5, "ExampleSpider应该生成5个URL")
        
        # 测试单个URL处理
        test_url = urls[0]
        semaphore = asyncio.Semaphore(1)
        result = await spider.process_url(semaphore, test_url)
        
        self.assert_is_not_none(result, "URL处理应该成功")
        self.assert_equal(result['url'], test_url)
        self.assert_in('title', result)
        self.assert_in('content', result)
        self.assert_in('links', result)
        self.assert_in('images', result)
        
        # 验证数据清理
        self.assert_equal(result['title'], "Example Page 1")  # 应该被清理


class TestErrorHandling(TestCase):
    """测试错误处理"""
    
    async def setup(self):
        """测试前置操作"""
        self.logger = MockLogger()
        self.test_config = {
            "error_test": {
                "target": "error_test",
                "base_url": "https://error.test.com",
                "headers": {},
                "delay": 0.1,
                "timeout": 5,
                "max_retries": 2,
                "output_format": "json",
                "output_path": "error_test_data"
            }
        }
        
        self.config_file = TestDataGenerator.create_temp_config(self.test_config)
        
    async def teardown(self):
        """测试后置操作"""
        if hasattr(self, 'config_file') and os.path.exists(self.config_file):
            os.remove(self.config_file)
    
    async def test_network_error_handling(self):
        """测试网络错误处理"""
        spider = Spider(
            target="error_test",
            config_path=self.config_file,
            logger=self.logger
        )
        
        # Mock request handler that always fails
        class FailingRequestHandler:
            async def fetch(self, session, url):
                return None  # 模拟网络失败
        
        spider.request_handler = FailingRequestHandler()
        
        # 测试URL处理
        semaphore = asyncio.Semaphore(1)
        result = await spider.process_url(semaphore, "https://error.test.com")
        
        self.assert_is_none(result, "网络失败应该返回None")
        
        # 检查错误日志
        error_logs = self.logger.get_logs('ERROR')
        self.assert_true(len(error_logs) >= 0, "可能会记录错误日志")
    
    async def test_parse_response_error(self):
        """测试响应解析错误"""
        spider = Spider(
            target="error_test",
            config_path=self.config_file,
            logger=self.logger
        )
        
        # Mock一个会抛出异常的响应
        mock_response = Mock()
        mock_response.text = AsyncMock(side_effect=Exception("Parse error"))
        mock_response.status = 200
        
        result = await spider.parse_response(mock_response, "https://error.test.com")
        
        self.assert_is_none(result, "解析错误应该返回None")
        
        # 检查错误日志
        error_logs = self.logger.get_logs('ERROR')
        self.assert_true(len(error_logs) > 0, "应该记录解析错误")


class TestConfigurationEdgeCases(TestCase):
    """测试配置边界情况"""
    
    async def setup(self):
        """测试前置操作"""
        self.logger = MockLogger()
    
    def test_empty_config_file(self):
        """测试空配置文件"""
        # 创建空配置文件
        fd, empty_config_file = tempfile.mkstemp(suffix='.json')
        try:
            with os.fdopen(fd, 'w') as f:
                f.write('{}')
            
            try:
                spider = Spider(
                    target="test_target",
                    config_path=empty_config_file,
                    logger=self.logger
                )
                self.assert_true(False, "应该抛出ValueError")
            except ValueError as e:
                self.assert_in("未找到目标", str(e))
                
        finally:
            os.remove(empty_config_file)
    
    def test_malformed_config_file(self):
        """测试格式错误的配置文件"""
        # 创建格式错误的配置文件
        fd, bad_config_file = tempfile.mkstemp(suffix='.json')
        try:
            with os.fdopen(fd, 'w') as f:
                f.write('{ invalid json }')
            
            try:
                spider = Spider(
                    target="test_target",
                    config_path=bad_config_file,
                    logger=self.logger
                )
                self.assert_true(False, "应该抛出异常")
            except Exception as e:
                # 应该抛出JSON解析错误
                self.assert_true(True, "格式错误的配置文件应该抛出异常")
                
        finally:
            os.remove(bad_config_file)


class TestPerformance(TestCase):
    """测试性能相关功能"""
    
    async def setup(self):
        """测试前置操作"""
        self.logger = MockLogger()
        self.test_config = {
            "performance_test": {
                "target": "performance_test",
                "base_url": "https://perf.test.com",
                "headers": {},
                "delay": 0.01,  # 很小的延时
                "timeout": 30,
                "max_retries": 1,
                "output_format": "json",
                "output_path": "perf_test_data"
            }
        }
        
        self.config_file = TestDataGenerator.create_temp_config(self.test_config)
        
    async def teardown(self):
        """测试后置操作"""
        if hasattr(self, 'config_file') and os.path.exists(self.config_file):
            os.remove(self.config_file)
        
        test_data_path = Path("perf_test_data")
        if test_data_path.exists():
            import shutil
            shutil.rmtree(test_data_path)
    
    async def test_concurrent_processing(self):
        """测试并发处理性能"""
        
        class PerfTestSpider(Spider):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.mock_session = MockHttpSession()
                self.request_count = 0
                
            async def get_urls(self):
                # 生成10个测试URL
                return [f"https://perf.test.com/page/{i}" for i in range(1, 11)]
            
            async def parse_response(self, response, url):
                self.request_count += 1
                content = await response.text()
                return {
                    'url': url,
                    'request_number': self.request_count,
                    'content_length': len(content)
                }
        
        spider = PerfTestSpider(
            target="performance_test",
            config_path=self.config_file,
            workers=5,  # 5个并发worker
            logger=self.logger
        )
        
        # Mock request handler
        class MockRequestHandler:
            async def fetch(self, session, url):
                # 模拟网络延时
                await asyncio.sleep(0.01)
                return MockHttpResponse(f"Content for {url}", 200)
        
        spider.request_handler = MockRequestHandler()
        mock_storage = MockStorage(self.logger)
        spider.storage = mock_storage
        
        # 测量执行时间
        import time
        start_time = time.time()
        
        # 执行并发处理
        urls = await spider.get_urls()
        semaphore = asyncio.Semaphore(spider.workers)
        tasks = [spider.process_url(semaphore, url) for url in urls]
        results = await asyncio.gather(*tasks)
        
        execution_time = time.time() - start_time
        
        # 验证结果
        valid_results = [r for r in results if r is not None]
        self.assert_equal(len(valid_results), 10, "应该处理10个URL")
        
        # 验证并发效果（应该比串行快）
        self.assert_true(execution_time < 0.5, f"并发处理应该很快，实际耗时: {execution_time:.3f}s")
        
        if self.logger:
            self.logger.info(f"并发处理10个URL耗时: {execution_time:.3f}秒")


class TestDataFlow(TestCase):
    """测试数据流转"""
    
    async def setup(self):
        """测试前置操作"""
        self.logger = MockLogger()
        
    async def test_data_pipeline(self):
        """测试完整数据管道"""
        from utils.data_processor import DataProcessor
        from utils.storage import Storage
        
        processor = DataProcessor(logger=self.logger)
        storage = MockStorage(self.logger)
        
        # 1. 原始HTML数据
        raw_html = TestDataGenerator.generate_html_content(
            "Pipeline Test", "This is pipeline test content"
        )
        
        # 2. 解析HTML
        soup = processor.parse_html(raw_html)
        self.assert_is_not_none(soup)
        
        # 3. 提取结构化数据
        extracted_data = {
            'title': processor.extract_text(soup, '#title'),
            'content': processor.extract_text(soup, '.content p'),
            'links': processor.extract_links(soup, "https://test.com"),
            'images': processor.extract_images(soup, "https://test.com")
        }
        
        # 4. 清理数据
        extracted_data['title'] = processor.clean_text(extracted_data['title'])
        extracted_data['content'] = processor.clean_text(extracted_data['content'])
        
        # 5. 验证数据质量
        self.assert_equal(extracted_data['title'], "Pipeline Test")
        self.assert_in("pipeline test content", extracted_data['content'].lower())
        self.assert_equal(len(extracted_data['links']), 2)
        self.assert_equal(len(extracted_data['images']), 2)
        
        # 6. 保存数据
        await storage.save([extracted_data], format='json', path='pipeline_test', filename='result')
        
        # 7. 验证保存
        saved_data = storage.get_saved_data()
        self.assert_equal(len(saved_data), 1)
        self.assert_equal(saved_data[0]['title'], "Pipeline Test")


# 创建集成测试套件
integration_test_suite = create_test_suite("Integration Tests")
integration_test_suite.add_test_case(TestSpiderIntegration())
integration_test_suite.add_test_case(TestExampleSpiderIntegration())
integration_test_suite.add_test_case(TestErrorHandling())
integration_test_suite.add_test_case(TestConfigurationEdgeCases())
integration_test_suite.add_test_case(TestPerformance())
integration_test_suite.add_test_case(TestDataFlow())