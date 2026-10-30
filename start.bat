@echo off
chcp 65001 >nul
echo ═══════════════════════════════════════════
echo    Telegram NFT Offers Bot
echo ═══════════════════════════════════════════
echo.

REM Проверка наличия Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python не установлен!
    echo Пожалуйста, установите Python с https://python.org
    pause
    exit /b 1
)

echo ✅ Python найден
echo.

REM Проверка наличия .env файла
if not exist ".env" (
    echo ⚠️  Файл .env не найден
    echo Создайте файл .env на основе .env.example
    echo.
    set /p token="Введите токен бота: "
    echo BOT_TOKEN=!token! > .env
    echo ALLOWED_USERS= >> .env
    echo ✅ Файл .env создан
    echo.
)

REM Установка зависимостей
echo 📦 Проверка зависимостей...
pip install -q -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Ошибка при установке зависимостей
    pause
    exit /b 1
)

echo ✅ Зависимости установлены
echo.
echo ═══════════════════════════════════════════
echo 🚀 Запуск бота...
echo ═══════════════════════════════════════════
echo.

python bot.py

pause
