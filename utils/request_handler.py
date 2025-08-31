#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
请求处理模块
"""

import asyncio
import aiohttp
from fake_useragent import UserAgent
from typing import Optional

class RequestHandler:
    """HTTP请求处理器"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.ua = UserAgent()
        
    async def fetch(self, session: aiohttp.ClientSession, url: str, 
                   method: str = 'GET', data=None, max_retries: int = 3) -> Optional[aiohttp.ClientResponse]:
        """发送HTTP请求"""
        for retry in range(max_retries):
            try:
                headers = {
                    'User-Agent': self.ua.random
                }
                
                async with session.request(method, url, data=data, headers=headers) as response:
                    if response.status == 200:
                        return response
                    elif response.status in [429, 503, 502, 504]:
                        wait_time = 2 ** retry
                        if self.logger:
                            self.logger.warning(f"状态码 {response.status}，等待 {wait_time} 秒后重试")
                        await asyncio.sleep(wait_time)
                    else:
                        if self.logger:
                            self.logger.error(f"请求失败，状态码: {response.status}")
                        break
                        
            except asyncio.TimeoutError:
                if self.logger:
                    self.logger.warning(f"请求超时，重试 {retry + 1}/{max_retries}")
                await asyncio.sleep(2 ** retry)
            except Exception as e:
                if self.logger:
                    self.logger.error(f"请求异常: {e}")
                await asyncio.sleep(2 ** retry)
                
        return None
    
    async def download_file(self, session: aiohttp.ClientSession, url: str, 
                          filepath: str) -> bool:
        """下载文件"""
        try:
            response = await self.fetch(session, url)
            if response:
                with open(filepath, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        f.write(chunk)
                return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"下载文件失败: {e}")
        return False