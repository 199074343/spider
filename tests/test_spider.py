#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Spider类单元测试
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
from tests.mocks import MockLogger, MockHttpSession, MockHttpResponse, TestDataGenerator, MockStorage
from spider import Spider, SpiderConfig


class TestSpiderConfig(TestCase):
    """测试SpiderConfig数据类"""
    
    def test_spider_config_creation(self):
        """测试SpiderConfig创建"""
        config = SpiderConfig(
            target="test_target",
            base_url="https://test.com",
            headers={"User-Agent": "test"},
            delay=2.0,
            timeout=60,
            max_retries=5,
            output_format="json",
            output_path="test_data"
        )
        
        self.assert_equal(config.target, "test_target")
        self.assert_equal(config.base_url, "https://test.com")
        self.assert_equal(config.delay, 2.0)
        self.assert_equal(config.timeout, 60)
        self.assert_equal(config.max_retries, 5)
        self.assert_equal(config.output_format, "json")
        self.assert_equal(config.output_path, "test_data")
    
    def test_spider_config_defaults(self):
        """测试SpiderConfig默认值"""
        config = SpiderConfig(
            target="test",
            base_url="https://test.com",
            headers={}
        )
        
        self.assert_equal(config.delay, 1.0)
        self.assert_equal(config.timeout, 30)
        self.assert_equal(config.max_retries, 3)
        self.assert_equal(config.output_format, "json")
        self.assert_equal(config.output_path, "data")


class TestSpider(TestCase):
    """测试Spider主类"""
    
    async def setup(self):
        """测试前置操作"""
        self.logger = MockLogger()
        self.test_config = {
            "test_target": {
                "target": "test_target",
                "base_url": "https://test.com",
                "headers": {"User-Agent": "test-agent"},
                "delay": 1.0,
                "timeout": 30,
                "max_retries": 3,
                "output_format": "json",
                "output_path": "test_data"
            }
        }
        
        # 创建临时配置文件
        self.config_file = TestDataGenerator.create_temp_config(self.test_config)
        
    async def teardown(self):
        """测试后置操作"""
        # 清理临时文件
        if hasattr(self, 'config_file') and os.path.exists(self.config_file):
            os.remove(self.config_file)
        
        # 清理测试数据目录
        test_data_path = Path("test_data")
        if test_data_path.exists():
            import shutil
            shutil.rmtree(test_data_path)
    
    def test_spider_initialization(self):
        """测试Spider初始化"""
        spider = Spider(
            target="test_target",
            config_path=self.config_file,
            workers=3,
            logger=self.logger
        )
        
        self.assert_equal(spider.target, "test_target")
        self.assert_equal(spider.workers, 3)
        self.assert_equal(spider.logger, self.logger)
        self.assert_equal(spider.config.target, "test_target")
        self.assert_equal(spider.config.base_url, "https://test.com")
    
    def test_spider_config_loading(self):
        """测试配置加载"""
        spider = Spider(
            target="test_target",
            config_path=self.config_file,
            logger=self.logger
        )
        
        config = spider.config
        self.assert_equal(config.target, "test_target")
        self.assert_equal(config.base_url, "https://test.com")
        self.assert_equal(config.headers["User-Agent"], "test-agent")
        self.assert_equal(config.delay, 1.0)
        self.assert_equal(config.timeout, 30)
    
    def test_spider_config_not_found(self):
        """测试配置文件不存在的情况"""
        spider = Spider(
            target="nonexistent_target",
            config_path="nonexistent_config.json",
            logger=self.logger
        )
        
        # 应该使用默认配置
        self.assert_equal(spider.config.target, "nonexistent_target")
        self.assert_equal(spider.config.base_url, "")
        
        # 检查日志中是否有警告
        warning_logs = self.logger.get_logs('WARNING')
        self.assert_true(len(warning_logs) > 0, "应该记录配置文件不存在的警告")
    
    def test_spider_invalid_target(self):
        """测试无效目标配置"""
        try:
            spider = Spider(
                target="invalid_target",
                config_path=self.config_file,
                logger=self.logger
            )
            self.assert_true(False, "应该抛出ValueError异常")
        except ValueError as e:
            self.assert_in("未找到目标", str(e))
    
    async def test_get_urls_default(self):
        """测试默认get_urls方法"""
        spider = Spider(
            target="test_target",
            config_path=self.config_file,
            logger=self.logger
        )
        
        urls = await spider.get_urls()
        self.assert_equal(len(urls), 1)
        self.assert_equal(urls[0], "https://test.com")
    
    async def test_parse_response_default(self):
        """测试默认parse_response方法"""
        spider = Spider(
            target="test_target",
            config_path=self.config_file,
            logger=self.logger
        )
        
        mock_response = MockHttpResponse(
            text="<html><body>Test content</body></html>",
            status=200
        )
        
        result = await spider.parse_response(mock_response, "https://test.com")
        
        self.assert_is_not_none(result)
        self.assert_equal(result['url'], "https://test.com")
        self.assert_equal(result['status'], 200)
        self.assert_in("Test content", result['content'])
    
    async def test_save_results(self):
        """测试结果保存"""
        spider = Spider(
            target="test_target",
            config_path=self.config_file,
            logger=self.logger
        )
        
        # 使用Mock存储器
        mock_storage = MockStorage(self.logger)
        spider.storage = mock_storage
        
        test_results = [
            {"url": "https://test.com/1", "title": "Test 1"},
            {"url": "https://test.com/2", "title": "Test 2"},
            None,  # 无效结果
            Exception("Error"),  # 异常结果
        ]
        
        await spider.save_results(test_results)
        
        # 验证只保存了有效结果
        saved_data = mock_storage.get_saved_data()
        self.assert_equal(len(saved_data), 2)
        self.assert_equal(saved_data[0]['title'], "Test 1")
        self.assert_equal(saved_data[1]['title'], "Test 2")
        
        # 验证保存调用
        save_calls = mock_storage.get_save_calls()
        self.assert_equal(len(save_calls), 1)
        self.assert_equal(save_calls[0]['format'], 'json')
        self.assert_equal(save_calls[0]['filename'], 'test_target_results')


class TestSpiderIntegration(TestCase):
    """测试Spider集成功能"""
    
    async def setup(self):
        """测试前置操作"""
        self.logger = MockLogger()
        self.test_config = {
            "integration_test": {
                "target": "integration_test",
                "base_url": "https://test.com",
                "headers": {"User-Agent": "test-agent"},
                "delay": 0.1,  # 快速测试
                "timeout": 10,
                "max_retries": 2,
                "output_format": "json",
                "output_path": "test_integration_data"
            }
        }
        
        self.config_file = TestDataGenerator.create_temp_config(self.test_config)
        
    async def teardown(self):
        """测试后置操作"""
        if hasattr(self, 'config_file') and os.path.exists(self.config_file):
            os.remove(self.config_file)
        
        # 清理测试数据
        test_data_path = Path("test_integration_data")
        if test_data_path.exists():
            import shutil
            shutil.rmtree(test_data_path)
    
    async def test_spider_full_workflow(self):
        """测试Spider完整工作流程"""
        
        class TestSpiderImpl(Spider):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.mock_session = MockHttpSession()
                
                # 设置Mock响应
                self.mock_session.set_response(
                    "https://test.com/page/1",
                    MockHttpResponse(TestDataGenerator.generate_html_content("Page 1", "Content 1"))
                )
                self.mock_session.set_response(
                    "https://test.com/page/2", 
                    MockHttpResponse(TestDataGenerator.generate_html_content("Page 2", "Content 2"))
                )
            
            async def get_urls(self):
                return ["https://test.com/page/1", "https://test.com/page/2"]
            
            async def parse_response(self, response, url):
                content = await response.text()
                return {
                    'url': url,
                    'content': content[:100],  # 截取前100字符
                    'status': response.status
                }
        
        spider = TestSpiderImpl(
            target="integration_test",
            config_path=self.config_file,
            workers=2,
            logger=self.logger
        )
        
        # 使用Mock存储器
        mock_storage = MockStorage(self.logger)
        spider.storage = mock_storage
        
        # Mock request_handler
        class MockRequestHandler:
            async def fetch(self, session, url):
                return await spider.mock_session.get(url)
        
        spider.request_handler = MockRequestHandler()
        
        # 运行爬虫（模拟session）
        urls = await spider.get_urls()
        self.assert_equal(len(urls), 2)
        
        # 模拟处理URL
        semaphore = asyncio.Semaphore(2)
        tasks = [spider.process_url(semaphore, url) for url in urls]
        results = await asyncio.gather(*tasks)
        
        # 验证结果
        valid_results = [r for r in results if r is not None]
        self.assert_equal(len(valid_results), 2)
        
        # 保存结果
        await spider.save_results(results)
        
        # 验证保存
        saved_data = mock_storage.get_saved_data()
        self.assert_equal(len(saved_data), 2)
        
        # 检查日志
        info_logs = self.logger.get_logs('INFO')
        self.assert_true(len(info_logs) > 0, "应该有信息日志")


# 创建测试套件
spider_test_suite = create_test_suite("Spider Core Tests")
spider_test_suite.add_test_case(TestSpiderConfig())
spider_test_suite.add_test_case(TestSpider())
spider_test_suite.add_test_case(TestSpiderIntegration())