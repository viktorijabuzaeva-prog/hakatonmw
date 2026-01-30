@echo off
chcp 65001 >nul
cd /d "%~dp0backend"

echo ========================================
echo   Запуск сервера анализа транскриптов
echo ========================================
echo.
echo Директория: %cd%
echo.

REM Проверка Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ОШИБКА: Python не найден!
    echo Установите Python с python.org
    pause
    exit /b 1
)

echo Python найден, запускаю сервер...
echo.
echo Сервер будет доступен по адресу:
echo   http://localhost:5000
echo.
echo Откройте frontend\index.html в браузере
echo для работы с интерфейсом.
echo.
echo Нажмите Ctrl+C для остановки сервера.
echo ========================================
echo.

python app.py

pause
