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

- 异步并发爬取
- 自动重试机制
- 多种输出格式（JSON、CSV、Excel）
- 灵活的配置系统
- 完整的日志记录
- 数据清洗和处理
- 图片链接提取
- 用户代理轮换

## 示例运行

```bash
# 运行示例爬虫
python example_spider.py
```