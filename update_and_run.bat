@echo off
chcp 65001 >nul
echo ========================================
echo   Обновление зависимостей и запуск
echo ========================================
echo.

cd /d "%~dp0backend"

echo [1/2] Обновление библиотек...
python -m pip install --upgrade openai flask flask-cors python-docx anthropic python-dotenv --quiet

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ОШИБКА: Не удалось обновить библиотеки
    echo Убедитесь, что Python установлен и доступен в PATH
    pause
    exit /b 1
)

echo [2/2] Запуск сервера...
echo.
echo ========================================
echo   Сервер запущен на http://localhost:5000
echo   Нажмите Ctrl+C для остановки
echo ========================================
echo.

python app.py

pause
