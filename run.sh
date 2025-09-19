#!/bin/bash
#
# Glassnode完整分析启动脚本
#

echo "======================================"
echo "Glassnode 完整分析系统"
echo "======================================"
echo ""
echo "请选择运行模式："
echo "1. 快速测试 (每类5个端点)"
echo "2. 完整分析 (643个端点，带输出管理)"
echo "3. 查看最近的分析结果"
echo ""

read -p "请输入选项 (1-3): " choice

case $choice in
    1)
        echo "运行快速测试..."
        python glassnode_advanced_analysis.py
        python generate_dashboard_data.py
        echo ""
        echo "完成！启动Dashboard:"
        echo "python -m http.server 8000"
        echo "打开 http://localhost:8000/dashboard_complete.html"
        ;;
        
    2)
        echo "运行完整分析..."
        python run_complete_with_output.py
        ;;
        
    3)
        # 查找最新的输出目录
        latest_output=$(ls -d output_* 2>/dev/null | sort -r | head -1)
        if [ -z "$latest_output" ]; then
            echo "没有找到输出目录"
        else
            echo "最新输出目录: $latest_output"
            echo ""
            echo "启动Dashboard服务器..."
            cd "$latest_output/dashboard"
            python -m http.server 8000
        fi
        ;;
        
    *)
        echo "无效选项"
        ;;
esac