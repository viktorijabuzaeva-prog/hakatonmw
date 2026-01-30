@echo off
chcp 65001 >nul
echo ========================================
echo UX Transcript Analysis System
echo Установка и запуск
echo ========================================
echo.

cd /d "%~dp0backend"

echo [1/3] Проверка Python...
python --version
if %errorlevel% neq 0 (
    echo ОШИБКА: Python не найден!
    echo Установите Python 3.8+ с https://python.org
    pause
    exit /b 1
)

echo.
echo [2/3] Установка зависимостей...
python -m pip install --upgrade pip
python -m pip install flask==3.0.0
python -m pip install flask-cors==4.0.0
python -m pip install python-docx==1.1.0
python -m pip install openai==1.7.0
python -m pip install anthropic==0.8.0
python -m pip install python-dotenv==1.0.0

if %errorlevel% neq 0 (
    echo ОШИБКА: Не удалось установить зависимости!
    pause
    exit /b 1
)

echo.
echo [3/3] Запуск сервера...
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║   Сервер запущен на http://localhost:5000                ║
echo ║   Откройте frontend\index.html в браузере                ║
echo ║   Нажмите Ctrl+C для остановки сервера                   ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

python app.py

pause
