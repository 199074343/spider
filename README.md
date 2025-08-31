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

## 🧪 测试功能 (新增)

项目包含完整的自定义单元测试框架:

### 快速测试
```bash
python verify_tests.py        # 验证测试系统
python quick_test.py          # 快速功能验证
python test_all.py            # 完整测试套件
```

### 分类测试
```bash
python run_tests.py --suite spider        # 核心爬虫测试
python run_tests.py --suite utils         # 工具模块测试
python run_tests.py --suite mobile        # 移动端测试
python run_tests.py --suite integration   # 集成测试
```

### 自动化测试
```bash
python test_automation.py ci              # CI管道测试
python test_automation.py smoke           # 冒烟测试
python test_automation.py coverage        # 覆盖率分析
```

### 测试特性
- **自定义测试框架** - 支持异步测试和丰富断言
- **Mock对象库** - 完整的HTTP、移动端、日志Mock
- **多格式报告** - HTML、JSON、JUnit XML格式
- **覆盖率分析** - 代码覆盖率统计和分析
- **CI/CD集成** - GitHub Actions自动化测试
- **性能测试** - 并发性能验证

详细的测试使用说明请参考 [TESTING_GUIDE.md](TESTING_GUIDE.md)