#!/bin/bash

# 移动端爬虫快速启动脚本

echo "🚀 移动端爬虫快速启动"
echo "=========================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

# 检查并安装依赖
echo "📦 检查Python依赖..."
python3 -c "import aiohttp, selenium, appium" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 安装Python依赖..."
    pip3 install -r requirements.txt
fi

# 检查环境
echo "🔍 检查移动端环境..."
python3 mobile_tools.py check

if [ $? -ne 0 ]; then
    echo "❌ 环境检查失败，请先运行: python3 setup_mobile.py"
    exit 1
fi

# 启动Appium服务器（后台运行）
echo "🔧 启动Appium服务器..."
python3 mobile_tools.py start-appium &
APPIUM_PID=$!

# 等待Appium启动
sleep 5

# 运行测试
echo "🧪 运行集成测试..."
python3 test_mobile_integration.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 移动端爬虫环境准备就绪!"
    echo ""
    echo "可以使用以下命令运行移动端爬虫:"
    echo "python3 main.py --target mobile_app --mobile --debug"
    echo "python3 main.py --target mobile_browser --mobile --debug"
    echo "python3 example_mobile_spider.py"
else
    echo "❌ 集成测试失败"
fi

# 清理
echo "🧹 清理后台进程..."
kill $APPIUM_PID 2>/dev/null

echo "完成!"