@echo off
title 电商数据可视化平台
echo ========================================
echo    电商数据可视化平台
echo ========================================
echo.

cd /d "%~dp0"

set PYTHON=C:\Users\湫\AppData\Local\Programs\Python\Python310\python.exe

if not exist "%PYTHON%" (
    echo [错误] 未找到Python
    echo 路径: %PYTHON%
    pause
    exit /b 1
)

if not exist "data\订单数据.xlsx" (
    echo 正在生成模拟数据...
    "%PYTHON%" data_generator.py
    echo.
)

echo 正在启动，请等待...
echo.

start "" "http://localhost:8501"
"%PYTHON%" -m streamlit run app.py --server.port 8501

echo.
pause
