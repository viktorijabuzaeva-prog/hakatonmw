@echo off
chcp 65001 >nul
echo ========================================
echo Перезапуск сервера
echo ========================================
echo.

cd /d "%~dp0backend"

echo Проверка настройки...
python check_setup.py

if %errorlevel% neq 0 (
    echo.
    echo Обнаружены проблемы. Исправьте их перед запуском.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Запуск сервера...
echo ========================================
echo.
echo Сервер запустится на http://localhost:5000
echo Нажмите Ctrl+C для остановки
echo.

python app.py

pause
