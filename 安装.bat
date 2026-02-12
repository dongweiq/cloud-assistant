@echo off
chcp 65001 > nul
title 云端小助理 - 安装程序

echo ================================================
echo        云端小助理 - 一键安装程序
echo ================================================
echo.

REM 检查Python
echo [1/3] 检查Python环境...
python --version > nul 2>&1
if errorlevel 1 (
    echo.
    echo [!] 未检测到Python
    echo.
    echo 请先安装Python 3.10或更高版本:
    echo 1. 访问 https://www.python.org/downloads/
    echo 2. 下载并安装Python（勾选"Add to PATH"选项）
    echo 3. 安装完成后重新运行此脚本
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo    Python版本: %PYVER%

REM 安装依赖
echo.
echo [2/3] 安装依赖包（首次安装约需3-5分钟）...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [错误] 依赖安装失败，请检查网络连接
    pause
    exit /b 1
)
echo    依赖安装完成

REM 创建快捷方式
echo.
echo [3/3] 创建桌面快捷方式...

set SCRIPT_DIR=%~dp0
set SHORTCUT_PATH=%USERPROFILE%\Desktop\云端小助理.lnk

powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%SHORTCUT_PATH%'); $SC.TargetPath = '%SCRIPT_DIR%启动.bat'; $SC.WorkingDirectory = '%SCRIPT_DIR%'; $SC.Description = '云端小助理 - AI办公助手'; $SC.Save()"

if exist "%SHORTCUT_PATH%" (
    echo    桌面快捷方式已创建
) else (
    echo    快捷方式创建失败，请手动运行 启动.bat
)

echo.
echo ================================================
echo              安装完成！
echo ================================================
echo.
echo 使用方法:
echo   方式1: 双击桌面的"云端小助理"快捷方式
echo   方式2: 双击当前目录的"启动.bat"
echo.
echo 首次使用请在"设置"页面配置大模型API Key
echo.

set /p START="是否现在启动？(Y/N): "
if /i "%START%"=="Y" (
    call 启动.bat
)

pause
