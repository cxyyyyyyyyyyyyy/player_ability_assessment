@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

::::: 切换到项目根目录（脚本位于 backend/ 下，上级目录即项目根目录）
cd /d "%~dp0.."

echo ========================================
echo   绿茵慧眼 - 球员能力评估系统
echo   一键启动脚本 (Windows)
echo ========================================
echo.

::::: 1. 检查 Python
echo [1/4] 检查 Python...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo   [ERROR] 未找到 Python，请先安装 Python 3.10 或以上版本
    echo   https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PY_VERSION=%%i
echo   [OK] Python: %PY_VERSION%
echo.

::::: 2. 检查依赖
echo [2/4] 检查依赖...
python -c "import fastapi, uvicorn, pandas, numpy, sklearn, pydantic, rapidocr_onnxruntime" 2>nul
if %errorlevel% neq 0 (
    echo   缺少核心依赖，正在安装...
    python -m pip install -r "%~dp0requirements.txt"
    if %errorlevel% neq 0 (
        echo   [WARN] pip install 失败，将尝试使用已有依赖启动
    )
)
echo   [OK] 依赖检查完成
echo.

::::: 3. 检查并清理端口
echo [3/4] 检查端口 8000...
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo   [WARN] 端口 8000 已被占用（可能是上次未清理的残留进程）
    echo   [INFO] 正在自动清理...
    for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
        taskkill /f /pid %%p >nul 2>&1
    )
    timeout /t 1 /nobreak >nul
    netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
    if %errorlevel% equ 0 (
        echo   [ERROR] 清理失败，请手动关闭占用 8000 端口的程序后重试
        pause
        exit /b 1
    )
    echo   [OK] 旧进程已清理，端口 8000 释放
) else (
    echo   [OK] 端口 8000 空闲
)
echo.

::::: 4. 启动服务
echo [4/4] 启动服务...
echo.
echo ========================================
echo   正在启动后端服务，请稍候...
echo   启动完成后请自行在浏览器打开：http://localhost:8000
echo   直接关闭本窗口即可停止服务并释放端口
echo ========================================
echo.

::::: 启动后端（前台运行：关窗口 = 停止服务）
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

::::: 服务停止后清理残留进程，确保端口释放
echo.
echo 服务已停止，正在确保端口释放...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /f /pid %%p >nul 2>&1
)
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo [WARN] 端口 8000 仍被占用，请手动检查
) else (
    echo [OK] 端口 8000 已释放
)
pause
