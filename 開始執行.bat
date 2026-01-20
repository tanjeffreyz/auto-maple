@echo off
chcp 65001
title Auto Maple 繁體中文啟動器

echo ==========================================
echo      歡迎使用 Auto Maple 自動練功助手
echo ==========================================
echo.

echo [1/3] 正在檢查 Python 環境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [錯誤] 找不到 Python！請先去官網下載安裝 Python 3。
    pause
    exit
)

echo [2/3] 正在檢查並安裝必要的程式庫...
echo       (第一次執行會比較久，請耐心等待)
python -m pip install -r requirements.txt

echo.
echo [3/3] 準備啟動程式...
echo       請記得先開啟楓之谷遊戲視窗！
echo.
pause

python main.py
pause
