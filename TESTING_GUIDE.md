# 🧪 爬虫项目测试指南

本项目实现了完整的自定义单元测试框架，支持异步测试、Mock对象、测试报告生成和覆盖率分析。

## 🏗️ 测试架构

### 核心组件
- **测试框架** (`tests/test_framework.py`) - 自定义异步测试框架
- **Mock对象** (`tests/mocks.py`) - 完整的Mock对象库
- **测试运行器** (`run_tests.py`) - 测试执行和报告生成
- **覆盖率分析** (`tests/coverage_analyzer.py`) - 代码覆盖率分析
- **自动化工具** (`test_automation.py`) - CI/CD集成工具

### 测试类型
1. **单元测试** - 测试独立组件功能
2. **集成测试** - 测试组件间协作
3. **性能测试** - 测试并发和性能
4. **移动端测试** - 测试Android自动化功能

## 🚀 快速开始

### 1. 运行所有测试
```bash
# 一键运行所有测试
python test_all.py

# 或分步运行
python quick_test.py          # 快速验证
python run_tests.py           # 运行所有测试套件
```

### 2. 运行特定测试套件
```bash
python run_tests.py --suite spider        # 核心爬虫测试
python run_tests.py --suite utils         # 工具模块测试  
python run_tests.py --suite mobile        # 移动端测试
python run_tests.py --suite integration   # 集成测试
```

### 3. 性能和覆盖率测试
```bash
python run_tests.py --performance         # 性能测试
python test_automation.py coverage        # 覆盖率分析
python test_automation.py ci              # 完整CI管道
```

## 📝 编写测试

### 基本测试用例
```python
from tests.test_framework import TestCase, create_test_suite

class MyTestCase(TestCase):
    async def setup(self):
        """测试前置操作"""
        self.test_data = "setup data"
    
    async def teardown(self):
        """测试后置操作"""
        # 清理资源
        pass
    
    def test_basic_function(self):
        """测试基本功能"""
        result = some_function()
        self.assert_equal(result, expected_value)
    
    async def test_async_function(self):
        """测试异步功能"""
        result = await some_async_function()
        self.assert_is_not_none(result)

# 创建测试套件
my_test_suite = create_test_suite("My Test Suite")
my_test_suite.add_test_case(MyTestCase())
```

### 使用Mock对象
```python
from tests.mocks import MockLogger, MockHttpSession, MockHttpResponse

class TestWithMocks(TestCase):
    async def setup(self):
        self.logger = MockLogger()
        self.session = MockHttpSession()
        
        # 设置Mock响应
        self.session.set_response(
            "https://test.com",
            MockHttpResponse("Test content", 200)
        )
    
    async def test_with_mock_session(self):
        """使用Mock会话测试"""
        response = await self.session.get("https://test.com")
        content = await response.text()
        
        self.assert_equal(content, "Test content")
        self.assert_equal(response.status, 200)
        
        # 验证请求记录
        requests = self.session.get_requests()
        self.assert_equal(len(requests), 1)
        self.assert_equal(requests[0]['url'], "https://test.com")
```

### 移动端测试
```python
from tests.mocks import MockAndroidEmulator, MockAppiumDriver

class TestMobileFeature(TestCase):
    async def setup(self):
        self.emulator = MockAndroidEmulator()
        self.driver = MockAppiumDriver()
    
    async def test_mobile_workflow(self):
        """测试移动端工作流程"""
        # 启动模拟器
        result = await self.emulator.start_emulator("test_avd")
        self.assert_true(result)
        
        # 连接设备
        result = await self.emulator.connect_device()
        self.assert_true(result)
        
        # 获取设备信息
        info = await self.emulator.get_device_info()
        self.assert_in('model', info)
```

## 🔧 断言方法

### 基本断言
```python
self.assert_true(condition, "错误信息")
self.assert_false(condition, "错误信息")
self.assert_equal(actual, expected, "错误信息")
self.assert_not_equal(actual, expected, "错误信息")
```

### 包含断言
```python
self.assert_in(item, container, "错误信息")
self.assert_not_in(item, container, "错误信息")
```

### 空值断言
```python
self.assert_is_none(value, "错误信息")
self.assert_is_not_none(value, "错误信息")
```

### 异常断言
```python
# 同步函数异常
self.assert_raises(ValueError, function_that_raises, arg1, arg2)

# 异步函数异常
await self.assert_raises_async(ValueError, async_function_that_raises, arg1, arg2)
```

## 📊 测试报告

### 报告格式
1. **HTML报告** - 可视化的详细报告 (`reports/test_report.html`)
2. **JSON报告** - 机器可读的结构化报告 (`reports/test_report.json`)
3. **JUnit XML** - CI/CD系统兼容格式 (`reports/test_results.xml`)

### 生成报告
```bash
# 生成HTML报告
python run_tests.py --output-format html

# 生成所有格式报告
python run_tests.py --output-format all

# 自定义报告目录
python run_tests.py --reports-dir custom_reports
```

## 📈 覆盖率分析

### 运行覆盖率分析
```bash
python test_automation.py coverage
```

### 覆盖率指标
- **文件覆盖率** - 有测试的源文件比例
- **测试代码比** - 测试数量与代码组件比例
- **未覆盖文件** - 缺少测试的源文件列表

## 🤖 持续集成

### GitHub Actions
项目包含完整的GitHub Actions配置 (`.github/workflows/tests.yml`):
- 多Python版本测试 (3.8-3.11)
- 自动依赖安装
- 移动端测试环境
- 测试报告上传

### CI命令
```bash
# 运行CI管道
python test_automation.py ci

# 冒烟测试（快速验证）
python test_automation.py smoke
```

## 🛠️ 测试工具

### 快速验证
```bash
python quick_test.py          # 验证测试框架基本功能
```

### 测试管理
```bash
python run_tests.py --help    # 查看所有测试选项
python run_tests.py --verbose # 详细输出模式
```

### 自动化测试
```bash
python test_automation.py ci  # 完整CI测试管道
python test_automation.py smoke --verbose # 冒烟测试
```

## 📁 测试文件结构

```
tests/
├── __init__.py                 # 测试模块初始化
├── test_framework.py           # 自定义测试框架
├── mocks.py                   # Mock对象库
├── test_config.json           # 测试配置
├── test_config_manager.py     # 测试配置管理
├── coverage_analyzer.py       # 覆盖率分析
├── test_spider.py            # Spider核心测试
├── test_utils.py             # 工具模块测试
├── test_mobile.py            # 移动端测试
└── test_integration.py       # 集成测试

reports/                       # 测试报告目录
├── test_report.html          # HTML测试报告
├── test_report.json          # JSON测试报告
├── test_results.xml          # JUnit XML报告
└── coverage_report.json      # 覆盖率报告
```

## 🎯 最佳实践

### 1. 测试命名
- 测试类: `TestXXX`
- 测试方法: `test_xxx`
- 描述性命名，清楚表达测试目的

### 2. 测试结构
- 使用`setup()`和`teardown()`管理测试环境
- 每个测试方法专注测试一个功能点
- 使用Mock对象隔离外部依赖

### 3. 异步测试
- 异步测试方法使用`async def`
- 使用`await`调用异步断言方法
- 合理使用`asyncio.sleep()`模拟延时

### 4. Mock策略
- 使用Mock对象替代外部服务
- 记录Mock调用以验证交互
- 设置合理的Mock返回值

### 5. 错误测试
- 测试正常流程和异常流程
- 使用`assert_raises`测试异常处理
- 验证错误日志记录

## 🔍 调试测试

### 查看详细输出
```bash
python run_tests.py --verbose
```

### 单独运行失败的测试
```bash
# 先运行所有测试找出失败的测试
python run_tests.py

# 然后运行特定套件
python run_tests.py --suite spider --verbose
```

### 检查测试日志
测试日志会显示在控制台和`logs/spider.log`文件中。

### 调试Mock对象
```python
# 在测试中打印Mock调用记录
print(mock_session.get_requests())
print(mock_logger.get_logs())
```

## 📋 测试清单

在添加新功能时，确保：

- [ ] 为新类编写测试用例
- [ ] 为新方法编写测试方法
- [ ] 测试正常和异常情况
- [ ] 使用Mock对象隔离依赖
- [ ] 添加性能测试（如适用）
- [ ] 更新集成测试
- [ ] 运行完整测试套件验证
- [ ] 检查覆盖率报告

## 🚨 故障排除

### 常见问题

1. **导入错误**
   - 检查Python路径设置
   - 确保所有依赖已安装

2. **异步测试失败**
   - 确保异步方法使用`async def`
   - 检查`await`关键字使用

3. **Mock对象问题**
   - 验证Mock设置是否正确
   - 检查Mock返回值类型

4. **文件路径问题**
   - 使用绝对路径或相对于项目根目录的路径
   - 确保测试临时文件被正确清理

### 获取帮助
```bash
python run_tests.py --help
python test_automation.py --help
python quick_test.py
```

这个测试系统为爬虫项目提供了全面的质量保证，支持开发过程中的持续测试和CI/CD集成。