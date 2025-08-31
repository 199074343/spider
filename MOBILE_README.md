# 移动端爬虫集成指南

本项目现已集成Android模拟器支持，可以爬取移动应用和移动网站数据。

## 功能特性

### 🚀 核心功能
- **Android模拟器集成** - 自动启动和管理Android虚拟设备
- **Appium自动化** - 支持移动应用和移动浏览器自动化
- **异步处理** - 非阻塞的移动端操作
- **截图支持** - 自动截图记录爬取过程
- **多格式输出** - JSON、CSV、Excel格式数据导出
- **完整日志** - 详细的移动端操作日志

### 📱 支持的爬取方式
1. **移动应用爬虫** - 直接操作Android应用界面
2. **移动浏览器爬虫** - 通过Chrome浏览器爬取移动网站
3. **混合模式** - 结合应用和浏览器的数据爬取

## 环境准备

### 1. 安装依赖
```bash
# 自动安装所有依赖
python setup_mobile.py

# 或手动安装
pip install -r requirements.txt
```

### 2. 安装Android SDK
1. 下载并安装 [Android Studio](https://developer.android.com/studio)
2. 通过SDK Manager安装以下组件：
   - Android SDK Platform-Tools
   - Android SDK Build-Tools  
   - Android Emulator
   - Android API Level 30+ (推荐)

### 3. 设置环境变量
```bash
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/tools/bin
```

### 4. 创建Android虚拟设备(AVD)
```bash
# 方式1: 使用工具脚本
python mobile_tools.py create-avd --avd-name test_avd

# 方式2: 使用Android Studio AVD Manager
# 打开Android Studio -> Tools -> AVD Manager -> Create Virtual Device
```

### 5. 安装Appium
```bash
# 全局安装Appium
npm install -g appium

# 安装UiAutomator2驱动
appium driver install uiautomator2
```

## 使用方法

### 环境检查
```bash
# 检查所有环境是否正确配置
python mobile_tools.py check
```

### 启动Appium服务器
```bash
# 启动Appium服务器（默认端口4723）
python mobile_tools.py start-appium

# 或指定端口
python mobile_tools.py start-appium --port 4725
```

### 运行移动端爬虫

#### 1. 命令行方式
```bash
# 移动应用爬虫
python main.py --target mobile_app --mobile --debug

# 移动浏览器爬虫  
python main.py --target mobile_browser --mobile --debug
```

#### 2. 直接运行示例
```bash
# 运行移动应用示例
python example_mobile_spider.py

# 运行移动浏览器示例
python example_mobile_spider.py browser
```

#### 3. 自定义移动端爬虫
```python
from mobile_spider import MobileSpider
from selenium.webdriver.common.by import By

class CustomMobileSpider(MobileSpider):
    async def execute_mobile_tasks(self):
        results = []
        
        # 等待页面加载
        await asyncio.sleep(3)
        
        # 点击按钮
        await self.appium_handler.click_element(By.ID, "com.app:id/button")
        
        # 提取数据
        title = await self.appium_handler.get_text(By.ID, "com.app:id/title")
        
        # 滚动收集数据
        list_data = await self.scroll_and_collect(
            lambda: self.extract_list_data(
                "//android.widget.ListView//android.widget.LinearLayout",
                {
                    'title': ".//android.widget.TextView[@resource-id='title']",
                    'desc': ".//android.widget.TextView[@resource-id='desc']"
                }
            ),
            max_scrolls=5
        )
        
        results.extend(list_data)
        return results
```

## 配置说明

### 移动应用配置 (`mobile_app`)
```json
{
  "mobile_app": {
    "target": "mobile_app",
    "avd_name": "test_avd",                    // AVD名称
    "emulator_port": 5554,                     // 模拟器端口
    "appium_server_url": "http://localhost:4723", // Appium服务器地址
    "platform_name": "Android",               // 平台名称
    "platform_version": "11.0",               // Android版本
    "device_name": "emulator-5554",            // 设备名称
    "automation_name": "UiAutomator2",         // 自动化引擎
    "app_package": "com.example.app",          // 应用包名
    "app_activity": "com.example.app.MainActivity", // 启动Activity
    "no_reset": true,                          // 不重置应用状态
    "new_command_timeout": 300,                // 命令超时时间
    "output_format": "json"                    // 输出格式
  }
}
```

### 移动浏览器配置 (`mobile_browser`)
```json
{
  "mobile_browser": {
    "target": "mobile_browser",
    "base_url": "https://m.example.com",       // 目标网站
    "app_package": "com.android.chrome",       // Chrome浏览器包名
    "app_activity": "com.google.android.apps.chrome.Main", // Chrome启动Activity
    "delay": 3.0,                              // 请求延时
    "output_format": "json"
  }
}
```

## 工具命令

### 环境管理
```bash
# 检查环境
python mobile_tools.py check

# 列出所有AVD
python mobile_tools.py list-avds

# 创建新AVD
python mobile_tools.py create-avd --avd-name my_avd

# 启动Appium服务器
python mobile_tools.py start-appium --port 4723
```

### 应用管理
```bash
# 安装APK到模拟器
python mobile_tools.py install-app --avd-name test_avd --apk-path /path/to/app.apk
```

## 常见元素定位方式

### Android应用元素
```python
# 通过resource-id定位
By.ID, "com.app:id/element_id"

# 通过文本定位
By.XPATH, "//android.widget.TextView[@text='按钮文本']"

# 通过类名定位
By.CLASS_NAME, "android.widget.Button"

# 通过XPath定位
By.XPATH, "//android.widget.ListView//android.widget.LinearLayout[1]"
```

### 移动网页元素
```python
# 标准Web元素定位
By.TAG_NAME, "h1"
By.CLASS_NAME, "article-title"
By.CSS_SELECTOR, ".content p"
By.XPATH, "//input[@placeholder='搜索']"
```

## 最佳实践

### 1. 性能优化
- 使用`workers=1`（移动端单线程处理）
- 适当设置延时避免过快操作
- 及时截图记录关键步骤

### 2. 稳定性保证
- 添加充足的等待时间
- 使用显式等待而非固定延时
- 实现重试机制

### 3. 数据完整性
- 滚动加载更多数据
- 截图保存操作证据
- 记录详细的操作日志

## 故障排除

### 常见问题

1. **模拟器启动失败**
   - 检查AVD是否存在: `python mobile_tools.py list-avds`
   - 检查Android SDK环境变量
   - 确保有足够的内存和存储空间

2. **Appium连接失败**
   - 确保Appium服务器已启动: `python mobile_tools.py start-appium`
   - 检查端口是否被占用
   - 验证设备连接: `adb devices`

3. **元素定位失败**
   - 使用`uiautomatorviewer`工具查看元素属性
   - 增加等待时间
   - 检查元素选择器是否正确

4. **应用启动失败**
   - 确认应用包名和Activity名称正确
   - 检查应用是否已安装
   - 查看Appium日志获取详细错误信息

### 调试技巧
```bash
# 开启详细日志
python main.py --target mobile_app --mobile --debug

# 查看设备列表
adb devices

# 查看设备日志
adb logcat

# 查看应用包名
adb shell pm list packages | grep 应用名
```

## 扩展开发

### 自定义移动端爬虫
1. 继承`MobileSpider`类
2. 重写`execute_mobile_tasks()`方法
3. 使用`AppiumHandler`进行元素操作
4. 使用`AndroidEmulator`进行设备管理

### 添加新的自动化功能
1. 在`AppiumHandler`中添加新方法
2. 在`MobileSpider`中集成新功能
3. 更新配置文件支持新参数

这个移动端集成为爬虫项目提供了强大的移动设备自动化能力，支持复杂的移动端数据采集任务。