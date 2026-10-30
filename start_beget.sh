#!/bin/bash

# Скрипт запуска бота на Beget
# Замените YOUR_LOGIN на ваш логин на Beget

echo "═══════════════════════════════════════════"
echo "   Telegram NFT Offers Bot"
echo "   Запуск на Beget.com"
echo "═══════════════════════════════════════════"
echo ""

# Определяем директорию скрипта
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Переходим в директорию проекта
cd "$SCRIPT_DIR"

# Проверяем наличие виртуального окружения
if [ ! -d "venv" ]; then
    echo "⚠️  Виртуальное окружение не найдено!"
    echo "Создаём виртуальное окружение..."
    python3 -m venv venv
    echo "✅ Виртуальное окружение создано"
fi

# Активируем виртуальное окружение
source venv/bin/activate

# Проверяем наличие зависимостей
echo "📦 Проверка зависимостей..."
pip install -q -r requirements.txt

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    echo "⚠️  Файл .env не найден!"
    echo "Создайте файл .env с токеном бота"
    echo ""
    echo "Пример содержимого .env:"
    echo "BOT_TOKEN=ваш_токен_от_BotFather"
    echo "ALLOWED_USERS="
    exit 1
fi

echo "✅ Все проверки пройдены"
echo ""
echo "═══════════════════════════════════════════"
echo "🚀 Запуск бота..."
echo "═══════════════════════════════════════════"
echo ""

# Запускаем бота
python bot.py
