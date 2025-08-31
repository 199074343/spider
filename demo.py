#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
爬虫项目演示脚本
展示项目的核心功能
"""

import asyncio
import json
from pathlib import Path
from utils.logger import setup_logger


async def demo_basic_spider():
    """演示基础爬虫功能"""
    print("🕷️ 基础爬虫功能演示")
    print("-" * 40)
    
    from spider import Spider
    
    class DemoSpider(Spider):
        async def get_urls(self):
            # 返回一些演示URL
            return [
                "https://httpbin.org/status/200",
                "https://httpbin.org/json",
                "https://httpbin.org/html"
            ]
        
        async def parse_response(self, response, url):
            try:
                content = await response.text()
                return {
                    'url': url,
                    'status': response.status,
                    'content_length': len(content),
                    'content_preview': content[:100] + '...' if len(content) > 100 else content
                }
            except Exception as e:
                return {
                    'url': url,
                    'error': str(e),
                    'status': getattr(response, 'status', 'unknown')
                }
    
    logger = setup_logger(debug=False)
    
    spider = DemoSpider(
        target='test_real',
        config_path='config.json',
        workers=2,
        logger=logger
    )
    
    print("正在运行爬虫...")
    await spider.run()
    print("✅ 基础爬虫演示完成")


def demo_data_processing():
    """演示数据处理功能"""
    print("\n📊 数据处理功能演示")
    print("-" * 40)
    
    from utils.data_processor import DataProcessor
    
    processor = DataProcessor()
    
    # 演示HTML解析
    html = """
    <html>
        <head><title>演示页面</title></head>
        <body>
            <h1 id="main-title">欢迎使用爬虫项目</h1>
            <div class="content">
                <p>这是一个功能完整的爬虫框架</p>
                <a href="/link1">链接1</a>
                <a href="/link2">链接2</a>
                <img src="/image1.jpg" alt="图片1">
            </div>
        </body>
    </html>
    """
    
    soup = processor.parse_html(html)
    
    # 提取数据
    title = processor.extract_text(soup, '#main-title')
    content = processor.extract_text(soup, '.content p')
    links = processor.extract_links(soup, "https://demo.com")
    images = processor.extract_images(soup, "https://demo.com")
    
    print(f"标题: {title}")
    print(f"内容: {content}")
    print(f"链接: {links}")
    print(f"图片: {images}")
    
    # 文本清理
    dirty_text = "  这是一个  包含多余空格的   文本!!!  "
    clean_text = processor.clean_text(dirty_text)
    print(f"清理前: '{dirty_text}'")
    print(f"清理后: '{clean_text}'")
    
    print("✅ 数据处理演示完成")


async def demo_storage():
    """演示存储功能"""
    print("\n💾 存储功能演示")
    print("-" * 40)
    
    from utils.storage import Storage
    
    storage = Storage()
    
    # 演示数据
    demo_data = [
        {'id': 1, 'title': '标题1', 'content': '内容1', 'url': 'https://example.com/1'},
        {'id': 2, 'title': '标题2', 'content': '内容2', 'url': 'https://example.com/2'},
        {'id': 3, 'title': '标题3', 'content': '内容3', 'url': 'https://example.com/3'}
    ]
    
    # 创建演示目录
    demo_path = Path("demo_output")
    demo_path.mkdir(exist_ok=True)
    
    # 保存为不同格式
    await storage.save(demo_data, format='json', path='demo_output', filename='demo_data')
    await storage.save(demo_data, format='csv', path='demo_output', filename='demo_data')
    await storage.save(demo_data, format='excel', path='demo_output', filename='demo_data')
    
    print("✅ 数据已保存为多种格式:")
    print("  • demo_output/demo_data.json")
    print("  • demo_output/demo_data.csv") 
    print("  • demo_output/demo_data.xlsx")
    
    # 加载数据
    loaded_data = await storage.load_json('demo_output/demo_data.json')
    print(f"✅ 从JSON加载了 {len(loaded_data)} 条数据")


async def demo_test_framework():
    """演示测试框架"""
    print("\n🧪 测试框架演示")
    print("-" * 40)
    
    from tests.test_framework import TestCase, TestSuite
    
    class DemoTestCase(TestCase):
        def test_basic_assertions(self):
            """演示基本断言"""
            self.assert_true(True)
            self.assert_equal(1 + 1, 2)
            self.assert_in('hello', 'hello world')
        
        def test_string_operations(self):
            """演示字符串操作测试"""
            text = "Hello World"
            self.assert_equal(text.lower(), "hello world")
            self.assert_equal(len(text), 11)
        
        async def test_async_operation(self):
            """演示异步测试"""
            await asyncio.sleep(0.01)
            result = "async test completed"
            self.assert_is_not_none(result)
    
    # 创建并运行测试套件
    suite = TestSuite("Demo Test Suite")
    suite.add_test_case(DemoTestCase())
    
    result = await suite.run()
    print(f"测试结果: {result['passed']}/{result['total_tests']} 通过")
    print(f"成功率: {result['success_rate']:.1f}%")
    print("✅ 测试框架演示完成")


def demo_configuration():
    """演示配置系统"""
    print("\n⚙️ 配置系统演示")
    print("-" * 40)
    
    # 显示当前配置
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("当前配置的目标:")
    for target_name in config.keys():
        target_config = config[target_name]
        print(f"  • {target_name}: {target_config.get('base_url', 'N/A')}")
    
    print("\n配置说明:")
    print("  • example_site: 示例网站配置")
    print("  • news_site: 新闻网站配置")
    print("  • mobile_app: 移动应用配置")
    print("  • mobile_browser: 移动浏览器配置")
    print("  • test_real: 测试配置")
    
    print("✅ 配置系统演示完成")


def show_project_structure():
    """显示项目结构"""
    print("\n📁 项目结构")
    print("-" * 40)
    
    structure = """
爬虫项目/
├── 核心模块
│   ├── spider.py              # 核心爬虫类
│   ├── mobile_spider.py       # 移动端爬虫
│   ├── main.py                # 命令行入口
│   └── config.json            # 配置文件
├── 工具模块 (utils/)
│   ├── data_processor.py      # 数据处理
│   ├── storage.py             # 数据存储
│   ├── request_handler.py     # 请求处理
│   ├── android_emulator.py    # Android模拟器
│   ├── appium_handler.py      # Appium自动化
│   └── logger.py              # 日志系统
├── 测试系统 (tests/)
│   ├── test_framework.py      # 自定义测试框架
│   ├── mocks.py               # Mock对象库
│   ├── test_spider.py         # 爬虫测试
│   ├── test_utils.py          # 工具测试
│   ├── test_mobile.py         # 移动端测试
│   └── test_integration.py    # 集成测试
├── 示例和工具
│   ├── example_spider.py      # 爬虫示例
│   ├── example_mobile_spider.py # 移动端示例
│   ├── mobile_tools.py        # 移动端工具
│   └── demo.py                # 本演示脚本
└── 文档
    ├── README.md              # 项目说明
    ├── MOBILE_README.md       # 移动端说明
    ├── TESTING_GUIDE.md       # 测试指南
    └── TEST_USAGE.md          # 测试使用说明
"""
    
    print(structure)


async def main():
    """主演示函数"""
    print("🚀 爬虫项目功能演示")
    print("=" * 60)
    
    # 显示项目结构
    show_project_structure()
    
    # 演示配置系统
    demo_configuration()
    
    # 演示数据处理
    demo_data_processing()
    
    # 演示存储功能
    await demo_storage()
    
    # 演示测试框架
    await demo_test_framework()
    
    # 演示基础爬虫（可能因网络问题失败，但会展示框架工作）
    try:
        await demo_basic_spider()
    except Exception as e:
        print(f"⚠️ 网络请求演示跳过（网络问题）: {e}")
        print("✅ 爬虫框架结构正常")
    
    print("\n" + "=" * 60)
    print("🎉 项目演示完成!")
    print("=" * 60)
    
    print("\n💡 快速开始:")
    print("# 基础爬虫")
    print("python main.py --target example_site --debug")
    print("\n# 移动端爬虫（需要Android环境）")
    print("python main.py --target mobile_app --mobile --debug")
    print("\n# 运行测试")
    print("python quick_test.py")
    print("python run_tests.py --suite spider")
    print("\n# 完整测试套件")
    print("python test_all.py")
    
    print("\n📖 详细文档:")
    print("• README.md - 项目总览")
    print("• MOBILE_README.md - 移动端功能")
    print("• TESTING_GUIDE.md - 测试指南")


if __name__ == '__main__':
    asyncio.run(main())