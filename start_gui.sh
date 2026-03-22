#!/bin/bash
# 漫画分镜自动切分工具 - 一键启动脚本 (Linux/macOS)

echo "========================================"
echo "   漫画分镜自动切分工具 - GUI版本"
echo "========================================"
echo

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python3，请先安装Python 3.7+"
    exit 1
fi

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "[信息] 虚拟环境不存在，正在创建..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[错误] 创建虚拟环境失败！"
        exit 1
    fi
    echo "[成功] 虚拟环境创建完成"
fi

# 激活虚拟环境
echo "[信息] 激活虚拟环境..."
source venv/bin/activate

# 检查依赖是否安装
echo "[信息] 检查依赖包..."
python -c "import cv2, numpy, PIL" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[信息] 正在安装依赖包..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[错误] 依赖安装失败！请检查网络连接"
        exit 1
    fi
    echo "[成功] 依赖安装完成"
fi

# 启动GUI
echo "[信息] 启动GUI界面..."
echo
python panel_detector_gui.py

# 如果GUI异常退出，保持窗口打开
if [ $? -ne 0 ]; then
    echo
    echo "[错误] 程序异常退出"
    read -p "按回车键继续..."
fi
