@echo off
chcp 65001 >nul
echo ========================================
echo   绿茵慧眼 - 停止服务
echo ========================================
echo.
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if %errorlevel% neq 0 (
    echo 端口 8000 没有服务在运行。
    pause
    exit /b 0
)
echo 正在停止占用 8000 端口的进程...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /f /pid %%p
)
timeout /t 1 /nobreak >nul
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo [WARN] 仍有进程占用 8000，请手动检查
) else (
    echo [OK] 端口 8000 已释放
)
pause
