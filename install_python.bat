@echo off
chcp 65001 >nul
echo ========================================
echo Установка Python 3.11
echo ========================================
echo.

echo Скачивание Python 3.11.9 (официальный установщик)...
echo.

set PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
set INSTALLER=python-installer.exe

echo Загрузка с: %PYTHON_URL%
echo.

powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%INSTALLER%'}"

if not exist "%INSTALLER%" (
    echo.
    echo ❌ ОШИБКА: Не удалось скачать установщик
    echo.
    echo Пожалуйста, установите Python вручную:
    echo 1. Откройте: https://www.python.org/downloads/
    echo 2. Скачайте Python 3.11 или выше
    echo 3. Запустите установщик
    echo 4. ВАЖНО: Поставьте галочку "Add Python to PATH"
    echo 5. Нажмите "Install Now"
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Запуск установщика...
echo ========================================
echo.
echo ВАЖНО:
echo 1. В установщике поставьте галочку "Add Python to PATH"
echo 2. Нажмите "Install Now"
echo 3. Дождитесь завершения установки
echo.

start /wait %INSTALLER%

echo.
echo Очистка...
del %INSTALLER%

echo.
echo ========================================
echo Проверка установки...
echo ========================================
echo.

python --version

if %errorlevel% equ 0 (
    echo.
    echo ✅ Python успешно установлен!
    echo.
    echo Теперь можете запустить: install_and_run.bat
    echo.
) else (
    echo.
    echo ⚠️  Python установлен, но не найден в PATH
    echo.
    echo Перезапустите командную строку или компьютер
    echo Затем запустите: install_and_run.bat
    echo.
)

pause
