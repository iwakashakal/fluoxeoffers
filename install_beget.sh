#!/bin/bash

# Скрипт установки бота на Beget
# Выполните этот скрипт один раз после загрузки файлов на сервер

echo "═══════════════════════════════════════════"
echo "   Установка Telegram NFT Offers Bot"
echo "   на Beget.com"
echo "═══════════════════════════════════════════"
echo ""

# Определяем директорию скрипта
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Шаг 1: Создание виртуального окружения
echo "📦 Шаг 1/4: Создание виртуального окружения..."
if [ -d "venv" ]; then
    echo "⚠️  Виртуальное окружение уже существует"
    read -p "Пересоздать? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        echo "✅ Виртуальное окружение пересоздано"
    fi
else
    python3 -m venv venv
    echo "✅ Виртуальное окружение создано"
fi

# Шаг 2: Активация виртуального окружения
echo ""
echo "🔧 Шаг 2/4: Активация виртуального окружения..."
source venv/bin/activate
echo "✅ Виртуальное окружение активировано"

# Шаг 3: Установка зависимостей
echo ""
echo "📥 Шаг 3/4: Установка зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Зависимости установлены"

# Шаг 4: Настройка .env файла
echo ""
echo "⚙️  Шаг 4/4: Настройка .env файла..."
if [ -f ".env" ]; then
    echo "⚠️  Файл .env уже существует"
    cat .env
    echo ""
    read -p "Пересоздать? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        read -p "Введите токен бота: " bot_token
        echo "BOT_TOKEN=$bot_token" > .env
        echo "ALLOWED_USERS=" >> .env
        echo "✅ Файл .env создан"
    fi
else
    echo ""
    read -p "Введите токен бота: " bot_token
    echo "BOT_TOKEN=$bot_token" > .env
    echo "ALLOWED_USERS=" >> .env
    echo "✅ Файл .env создан"
fi

# Шаг 5: Установка прав
echo ""
echo "🔐 Установка прав на файлы..."
chmod +x start_beget.sh
chmod +x install_beget.sh
chmod 600 .env  # Только владелец может читать .env
echo "✅ Права установлены"

# Финал
echo ""
echo "═══════════════════════════════════════════"
echo "✅ Установка завершена!"
echo "═══════════════════════════════════════════"
echo ""
echo "Для запуска бота используйте:"
echo ""
echo "1. Через screen (рекомендуется):"
echo "   screen -S telegram_bot"
echo "   ./start_beget.sh"
echo "   Ctrl+A, затем D (для отключения)"
echo ""
echo "2. Напрямую (для тестирования):"
echo "   ./start_beget.sh"
echo ""
echo "3. В фоне через nohup:"
echo "   nohup ./start_beget.sh > bot.log 2>&1 &"
echo ""
echo "Для просмотра логов:"
echo "   tail -f bot.log"
echo ""
echo "Для подключения к screen:"
echo "   screen -r telegram_bot"
echo ""
echo "═══════════════════════════════════════════"
