#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
核心爬虫类
"""

import asyncio
import aiohttp
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from utils.request_handler import RequestHandler
from utils.data_processor import DataProcessor
from utils.storage import Storage

@dataclass
class SpiderConfig:
    """爬虫配置类"""
    target: str
    base_url: str
    headers: Dict[str, str]
    delay: float = 1.0
    timeout: int = 30
    max_retries: int = 3
    output_format: str = 'json'
    output_path: str = 'data'

class Spider:
    """主爬虫类"""
    
    def __init__(self, target: str, config_path: str = 'config.json', 
                 workers: int = 5, logger=None):
        self.target = target
        self.workers = workers
        self.logger = logger
        self.config = self._load_config(config_path)
        self.request_handler = RequestHandler(logger=logger)
        self.data_processor = DataProcessor(logger=logger)
        self.storage = Storage(logger=logger)
        self.session = None
        self.tasks = []
        
    def _load_config(self, config_path: str) -> SpiderConfig:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                
            target_config = config_data.get(self.target)
            if not target_config:
                raise ValueError(f"配置文件中未找到目标 '{self.target}' 的配置")
                
            return SpiderConfig(**target_config)
        except FileNotFoundError:
            if self.logger:
                self.logger.warning(f"配置文件 {config_path} 不存在，使用默认配置")
            return SpiderConfig(
                target=self.target,
                base_url="",
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
        except Exception as e:
            if self.logger:
                self.logger.error(f"加载配置文件失败: {e}")
            raise
    
    async def run(self):
        """运行爬虫"""
        if self.logger:
            self.logger.info(f"开始爬取目标: {self.target}")
            
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            headers=self.config.headers
        ) as session:
            self.session = session
            
            # 获取任务列表
            urls = await self.get_urls()
            if self.logger:
                self.logger.info(f"获取到 {len(urls)} 个URL")
            
            # 创建信号量控制并发
            semaphore = asyncio.Semaphore(self.workers)
            
            # 创建任务
            tasks = [self.process_url(semaphore, url) for url in urls]
            
            # 执行任务
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理结果
            await self.save_results(results)
            
        if self.logger:
            self.logger.info("爬虫任务完成")
    
    async def get_urls(self) -> List[str]:
        """获取要爬取的URL列表，子类应重写此方法"""
        # 这里应该根据具体需求实现URL获取逻辑
        return [self.config.base_url]
    
    async def process_url(self, semaphore: asyncio.Semaphore, url: str):
        """处理单个URL"""
        async with semaphore:
            try:
                if self.logger:
                    self.logger.debug(f"开始处理URL: {url}")
                
                # 发送请求
                response = await self.request_handler.fetch(self.session, url)
                if not response:
                    return None
                
                # 处理数据
                data = await self.parse_response(response, url)
                
                # 延时
                if self.config.delay > 0:
                    await asyncio.sleep(self.config.delay)
                
                return data
                
            except Exception as e:
                if self.logger:
                    self.logger.error(f"处理URL {url} 时出错: {e}")
                return None
    
    async def parse_response(self, response: aiohttp.ClientResponse, url: str):
        """解析响应，子类应重写此方法"""
        try:
            content = await response.text()
            return {
                'url': url,
                'content': content,
                'status': response.status
            }
        except Exception as e:
            if self.logger:
                self.logger.error(f"解析响应失败: {e}")
            return None
    
    async def save_results(self, results: List):
        """保存结果"""
        valid_results = [r for r in results if r is not None and not isinstance(r, Exception)]
        
        if valid_results:
            await self.storage.save(
                data=valid_results,
                format=self.config.output_format,
                path=self.config.output_path,
                filename=f"{self.target}_results"
            )
            
            if self.logger:
                self.logger.info(f"保存了 {len(valid_results)} 条有效数据")
        else:
            if self.logger:
                self.logger.warning("没有有效数据可保存")