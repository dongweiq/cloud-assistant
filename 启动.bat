@echo off
chcp 65001 > nul
title 云端小助理

echo ================================================
echo           云端小助理 - 启动器
echo ================================================
echo.

REM 检查Python
python --version > nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.10+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查依赖
echo 检查依赖...
pip show streamlit > nul 2>&1
if errorlevel 1 (
    echo 首次运行，正在安装依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
)

echo.
echo 启动云端小助理...
echo 请在浏览器中访问显示的地址
echo 按 Ctrl+C 可停止服务
echo.

streamlit run app_v2.py --server.headless true

pause
