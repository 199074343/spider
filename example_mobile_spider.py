#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
移动端爬虫示例实现
"""

import asyncio
import time
from typing import Dict, List, Any
from selenium.webdriver.common.by import By

from mobile_spider import MobileSpider, MobileSpiderFactory
from utils.logger import setup_logger


class MobileAppSpider(MobileSpider):
    """移动应用爬虫示例"""
    
    async def execute_mobile_tasks(self) -> List[Dict[str, Any]]:
        """执行移动应用爬取任务"""
        results = []
        
        try:
            if self.logger:
                self.logger.info("开始爬取移动应用数据")
            
            # 等待应用完全加载
            await asyncio.sleep(5)
            
            # 示例：爬取应用主页信息
            main_data = await self._scrape_main_page()
            if main_data:
                results.append(main_data)
            
            # 示例：爬取列表页数据
            list_data = await self._scrape_list_data()
            results.extend(list_data)
            
            # 示例：爬取详情页数据
            detail_data = await self._scrape_detail_pages()
            results.extend(detail_data)
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"移动应用爬取失败: {e}")
        
        return results
    
    async def _scrape_main_page(self) -> Dict[str, Any]:
        """爬取主页数据"""
        try:
            # 截图
            screenshot_path = f"screenshots/{self.target}_main.png"
            await self.appium_handler.take_screenshot(screenshot_path)
            
            # 获取页面源码
            page_source = await self.appium_handler.get_page_source()
            
            # 提取主要信息
            title = await self.appium_handler.get_text(By.ID, "com.example.app:id/title")
            subtitle = await self.appium_handler.get_text(By.ID, "com.example.app:id/subtitle")
            
            return {
                'page_type': 'main',
                'title': title,
                'subtitle': subtitle,
                'screenshot': screenshot_path,
                'timestamp': time.time()
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"爬取主页失败: {e}")
            return {}
    
    async def _scrape_list_data(self) -> List[Dict[str, Any]]:
        """爬取列表数据"""
        try:
            # 导航到列表页
            if await self.appium_handler.click_element(By.ID, "com.example.app:id/list_tab"):
                await asyncio.sleep(2)
                
                # 定义列表项选择器
                item_selectors = {
                    'title': ".//android.widget.TextView[@resource-id='com.example.app:id/item_title']",
                    'description': ".//android.widget.TextView[@resource-id='com.example.app:id/item_desc']",
                    'price': ".//android.widget.TextView[@resource-id='com.example.app:id/item_price']"
                }
                
                # 滚动并收集数据
                results = await self.scroll_and_collect(
                    lambda: self.extract_list_data(
                        "//android.widget.ListView/android.widget.LinearLayout",
                        item_selectors
                    ),
                    max_scrolls=5
                )
                
                # 为每条数据添加页面类型
                for item in results:
                    item['page_type'] = 'list_item'
                    item['timestamp'] = time.time()
                
                return results
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"爬取列表数据失败: {e}")
        
        return []
    
    async def _scrape_detail_pages(self) -> List[Dict[str, Any]]:
        """爬取详情页数据"""
        results = []
        
        try:
            # 点击第一个列表项进入详情页
            if await self.appium_handler.click_element(
                By.XPATH, 
                "//android.widget.ListView/android.widget.LinearLayout[1]"
            ):
                await asyncio.sleep(3)
                
                # 提取详情页信息
                detail_title = await self.appium_handler.get_text(By.ID, "com.example.app:id/detail_title")
                detail_content = await self.appium_handler.get_text(By.ID, "com.example.app:id/detail_content")
                detail_images = await self._extract_image_urls()
                
                # 截图
                screenshot_path = f"screenshots/{self.target}_detail.png"
                await self.appium_handler.take_screenshot(screenshot_path)
                
                detail_data = {
                    'page_type': 'detail',
                    'title': detail_title,
                    'content': detail_content,
                    'images': detail_images,
                    'screenshot': screenshot_path,
                    'timestamp': time.time()
                }
                
                results.append(detail_data)
                
                # 返回列表页
                await self.appium_handler.click_element(By.ID, "com.example.app:id/back_button")
                await asyncio.sleep(2)
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"爬取详情页失败: {e}")
        
        return results
    
    async def _extract_image_urls(self) -> List[str]:
        """提取图片URL"""
        try:
            image_elements = await self.appium_handler.find_elements(
                By.XPATH, 
                "//android.widget.ImageView"
            )
            
            image_urls = []
            for element in image_elements:
                # 获取图片相关属性
                content_desc = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: element.get_attribute("content-desc")
                )
                if content_desc and content_desc.startswith('http'):
                    image_urls.append(content_desc)
            
            return image_urls
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"提取图片URL失败: {e}")
            return []


class MobileBrowserSpider(MobileSpider):
    """移动浏览器爬虫示例"""
    
    async def execute_mobile_tasks(self) -> List[Dict[str, Any]]:
        """执行移动浏览器爬取任务"""
        results = []
        
        try:
            if self.logger:
                self.logger.info("开始移动浏览器爬取")
            
            # 导航到目标网站
            if await self.navigate_to_url(self.mobile_config.base_url):
                
                # 等待页面加载
                await asyncio.sleep(5)
                
                # 爬取页面数据
                page_data = await self._scrape_mobile_page()
                if page_data:
                    results.append(page_data)
                
                # 爬取搜索结果
                search_results = await self._perform_search_and_scrape("Python爬虫")
                results.extend(search_results)
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"移动浏览器爬取失败: {e}")
        
        return results
    
    async def _scrape_mobile_page(self) -> Dict[str, Any]:
        """爬取移动页面数据"""
        try:
            # 获取页面标题
            title = await self.appium_handler.get_text(By.TAG_NAME, "h1")
            
            # 获取页面内容
            content_elements = await self.appium_handler.find_elements(By.TAG_NAME, "p")
            content = []
            
            for element in content_elements[:5]:  # 只取前5个段落
                text = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: element.text
                )
                if text:
                    content.append(text)
            
            # 截图
            screenshot_path = f"screenshots/{self.target}_page.png"
            await self.appium_handler.take_screenshot(screenshot_path)
            
            return {
                'page_type': 'mobile_page',
                'url': self.mobile_config.base_url,
                'title': title,
                'content': content,
                'screenshot': screenshot_path,
                'timestamp': time.time()
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"爬取移动页面失败: {e}")
            return {}
    
    async def _perform_search_and_scrape(self, keyword: str) -> List[Dict[str, Any]]:
        """执行搜索并爬取结果"""
        results = []
        
        try:
            # 查找搜索框
            search_box = await self.appium_handler.find_element(
                By.XPATH, 
                "//input[@type='search'] | //input[@name='q'] | //input[@placeholder*='搜索']"
            )
            
            if search_box:
                # 输入搜索关键词
                await self.appium_handler.input_text(
                    By.XPATH, 
                    "//input[@type='search'] | //input[@name='q'] | //input[@placeholder*='搜索']",
                    keyword
                )
                
                # 点击搜索按钮或回车
                await self.appium_handler.click_element(
                    By.XPATH,
                    "//button[@type='submit'] | //input[@type='submit']"
                )
                
                # 等待搜索结果加载
                await asyncio.sleep(5)
                
                # 提取搜索结果
                search_results = await self._extract_search_results()
                results.extend(search_results)
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"搜索爬取失败: {e}")
        
        return results
    
    async def _extract_search_results(self) -> List[Dict[str, Any]]:
        """提取搜索结果"""
        results = []
        
        try:
            # 查找搜索结果项
            result_elements = await self.appium_handler.find_elements(
                By.XPATH,
                "//div[contains(@class, 'result')] | //li[contains(@class, 'search')] | //article"
            )
            
            for i, element in enumerate(result_elements[:10]):  # 只取前10个结果
                try:
                    title = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: element.find_element(By.TAG_NAME, "h2").text if element.find_elements(By.TAG_NAME, "h2") else element.find_element(By.TAG_NAME, "h3").text if element.find_elements(By.TAG_NAME, "h3") else ""
                    )
                    
                    description = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: element.find_element(By.TAG_NAME, "p").text if element.find_elements(By.TAG_NAME, "p") else ""
                    )
                    
                    link = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: element.find_element(By.TAG_NAME, "a").get_attribute("href") if element.find_elements(By.TAG_NAME, "a") else ""
                    )
                    
                    result_data = {
                        'page_type': 'search_result',
                        'index': i,
                        'title': title,
                        'description': description,
                        'link': link,
                        'timestamp': time.time()
                    }
                    
                    results.append(result_data)
                    
                except Exception as e:
                    if self.logger:
                        self.logger.warning(f"提取搜索结果项 {i} 失败: {e}")
                    continue
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"提取搜索结果失败: {e}")
        
        return results


# 使用示例
async def run_mobile_app_example():
    """运行移动应用爬虫示例"""
    logger = setup_logger(debug=True)
    
    # 创建移动应用爬虫
    spider = MobileSpiderFactory.create_app_spider(
        target='mobile_app',
        app_package='com.example.app',
        app_activity='com.example.app.MainActivity',
        logger=logger
    )
    
    await spider.run()


async def run_mobile_browser_example():
    """运行移动浏览器爬虫示例"""
    logger = setup_logger(debug=True)
    
    # 创建移动浏览器爬虫
    spider = MobileBrowserSpider(
        target='mobile_browser',
        config_path='config.json',
        workers=1,
        logger=logger
    )
    
    await spider.run()


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'browser':
        # 运行浏览器爬虫
        asyncio.run(run_mobile_browser_example())
    else:
        # 运行应用爬虫
        asyncio.run(run_mobile_app_example())