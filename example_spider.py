#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
示例爬虫实现
"""

from spider import Spider
from utils.data_processor import DataProcessor
import aiohttp
from typing import List

class ExampleSpider(Spider):
    """示例网站爬虫"""
    
    async def get_urls(self) -> List[str]:
        """获取要爬取的URL列表"""
        # 这里可以从sitemap、列表页或API获取URL
        urls = [
            f"{self.config.base_url}/page/{i}" 
            for i in range(1, 6)  # 爬取前5页
        ]
        return urls
    
    async def parse_response(self, response: aiohttp.ClientResponse, url: str):
        """解析网页内容"""
        try:
            content = await response.text()
            
            # 解析HTML
            soup = self.data_processor.parse_html(content)
            if not soup:
                return None
            
            # 提取数据
            data = {
                'url': url,
                'title': self.data_processor.extract_text(soup, 'h1'),
                'content': self.data_processor.extract_text(soup, '.content'),
                'links': self.data_processor.extract_links(soup, self.config.base_url),
                'images': self.data_processor.extract_images(soup, self.config.base_url)
            }
            
            # 清理文本
            data['title'] = self.data_processor.clean_text(data['title'])
            data['content'] = self.data_processor.clean_text(data['content'])
            
            return data
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"解析响应失败 {url}: {e}")
            return None

# 使用示例
if __name__ == '__main__':
    import asyncio
    from utils.logger import setup_logger
    
    logger = setup_logger(debug=True)
    spider = ExampleSpider(
        target='example_site',
        config_path='config.json',
        workers=3,
        logger=logger
    )
    
    asyncio.run(spider.run())