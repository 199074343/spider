#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据处理模块
"""

import re
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional

class DataProcessor:
    """数据处理器"""
    
    def __init__(self, logger=None):
        self.logger = logger
    
    def parse_html(self, html: str, parser: str = 'lxml') -> Optional[BeautifulSoup]:
        """解析HTML"""
        try:
            return BeautifulSoup(html, parser)
        except Exception as e:
            if self.logger:
                self.logger.error(f"HTML解析失败: {e}")
            return None
    
    def extract_text(self, soup: BeautifulSoup, selector: str = None) -> str:
        """提取文本内容"""
        try:
            if selector:
                element = soup.select_one(selector)
                return element.get_text(strip=True) if element else ""
            else:
                return soup.get_text(strip=True)
        except Exception as e:
            if self.logger:
                self.logger.error(f"文本提取失败: {e}")
            return ""
    
    def extract_links(self, soup: BeautifulSoup, base_url: str = "") -> List[str]:
        """提取链接"""
        links = []
        try:
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('http'):
                    links.append(href)
                elif base_url and href.startswith('/'):
                    links.append(base_url.rstrip('/') + href)
        except Exception as e:
            if self.logger:
                self.logger.error(f"链接提取失败: {e}")
        return links
    
    def extract_images(self, soup: BeautifulSoup, base_url: str = "") -> List[str]:
        """提取图片链接"""
        images = []
        try:
            for img in soup.find_all('img', src=True):
                src = img['src']
                if src.startswith('http'):
                    images.append(src)
                elif base_url and src.startswith('/'):
                    images.append(base_url.rstrip('/') + src)
        except Exception as e:
            if self.logger:
                self.logger.error(f"图片提取失败: {e}")
        return images
    
    def clean_text(self, text: str) -> str:
        """清理文本"""
        if not text:
            return ""
        
        # 去除多余空白字符
        text = re.sub(r'\s+', ' ', text)
        # 去除首尾空白
        text = text.strip()
        # 去除特殊字符
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
        
        return text
    
    def extract_by_rules(self, soup: BeautifulSoup, rules: Dict[str, str]) -> Dict[str, Any]:
        """根据规则提取数据"""
        result = {}
        
        for key, selector in rules.items():
            try:
                element = soup.select_one(selector)
                if element:
                    result[key] = element.get_text(strip=True)
                else:
                    result[key] = ""
            except Exception as e:
                if self.logger:
                    self.logger.error(f"规则 {key} 提取失败: {e}")
                result[key] = ""
        
        return result