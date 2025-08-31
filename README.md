# Python 爬虫项目

一个功能完整的异步爬虫框架，支持多种数据格式输出和灵活的配置。

## 项目结构

```
spider/
├── main.py              # 主入口文件
├── spider.py            # 核心爬虫类
├── example_spider.py    # 示例爬虫实现
├── config.json          # 配置文件
├── requirements.txt     # 依赖包
├── utils/              # 工具模块
│   ├── __init__.py
│   ├── request_handler.py    # 请求处理
│   ├── data_processor.py     # 数据处理
│   ├── storage.py           # 数据存储
│   └── logger.py            # 日志工具
├── data/               # 数据输出目录
└── logs/              # 日志文件目录
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 命令行方式

```bash
# 基本使用
python main.py --target example_site

# 指定配置文件和并发数
python main.py --target news_site --config config.json --workers 10

# 开启调试模式
python main.py --target example_site --debug
```

### 2. 自定义爬虫

继承 `Spider` 类并重写关键方法：

```python
from spider import Spider

class CustomSpider(Spider):
    async def get_urls(self):
        # 返回要爬取的URL列表
        return ['url1', 'url2', 'url3']
    
    async def parse_response(self, response, url):
        # 解析响应内容
        content = await response.text()
        # 处理数据...
        return processed_data
```

## 配置说明

在 `config.json` 中配置不同的目标网站：

```json
{
  "target_name": {
    "target": "目标名称",
    "base_url": "基础URL",
    "headers": {
      "User-Agent": "用户代理"
    },
    "delay": 1.0,
    "timeout": 30,
    "max_retries": 3,
    "output_format": "json",
    "output_path": "data"
  }
}
```

## 功能特性

### 🌐 Web爬虫功能
- 异步并发爬取
- 自动重试机制
- 多种输出格式（JSON、CSV、Excel）
- 灵活的配置系统
- 完整的日志记录
- 数据清洗和处理
- 图片链接提取
- 用户代理轮换

### 📱 移动端爬虫功能 (新增)
- **Android模拟器集成** - 自动管理Android虚拟设备
- **Appium自动化** - 支持移动应用和移动浏览器
- **移动端数据爬取** - 原生应用界面操作和数据提取
- **截图记录** - 自动截图记录爬取过程
- **滚动收集** - 支持列表滚动和无限加载数据收集
- **移动浏览器支持** - 通过Chrome浏览器爬取移动网站

## 示例运行

### Web爬虫
```bash
# 运行示例爬虫
python example_spider.py

# 命令行方式
python main.py --target example_site --workers 5 --debug
```

### 移动端爬虫 (新增)
```bash
# 环境检查和设置
python setup_mobile.py                    # 安装移动端依赖
python mobile_tools.py check              # 检查环境
python mobile_tools.py start-appium       # 启动Appium服务器

# 运行移动端爬虫
python main.py --target mobile_app --mobile --debug        # 移动应用爬虫
python main.py --target mobile_browser --mobile --debug    # 移动浏览器爬虫

# 运行移动端示例
python example_mobile_spider.py           # 移动应用示例
python example_mobile_spider.py browser   # 移动浏览器示例

# 测试移动端集成
python test_mobile_integration.py         # 完整集成测试
```

详细的移动端使用说明请参考 [MOBILE_README.md](MOBILE_README.md)