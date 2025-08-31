#!/bin/bash

# 爬虫项目启动脚本

echo "🚀 爬虫项目启动脚本"
echo "===================="

# 检查虚拟环境
if [[ "$VIRTUAL_ENV" != *"spider_env"* ]]; then
    echo "📦 激活虚拟环境..."
    source spider_env/bin/activate
fi

echo "✅ 虚拟环境已激活: $VIRTUAL_ENV"

# 显示选项菜单
echo ""
echo "请选择要执行的操作:"
echo "1) 运行功能演示"
echo "2) 运行基础爬虫示例"
echo "3) 运行快速测试"
echo "4) 运行完整测试套件"
echo "5) 检查移动端环境"
echo "6) 查看项目状态"
echo "7) 退出"

read -p "请输入选择 (1-7): " choice

case $choice in
    1)
        echo "🎭 运行功能演示..."
        python demo.py
        ;;
    2)
        echo "🕷️ 运行基础爬虫示例..."
        python example_spider.py
        ;;
    3)
        echo "🧪 运行快速测试..."
        python quick_test.py
        ;;
    4)
        echo "🔍 运行完整测试套件..."
        python test_all.py
        ;;
    5)
        echo "📱 检查移动端环境..."
        python mobile_tools.py check
        ;;
    6)
        echo "📊 查看项目状态..."
        cat PROJECT_STATUS.md
        ;;
    7)
        echo "👋 再见！"
        exit 0
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "✅ 操作完成！"
echo "💡 提示: 可以直接运行 ./start.sh 重新选择操作"