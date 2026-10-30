# 🚀 Установка бота на Beget.com

## 📋 Что нужно перед началом

- ✅ Аккаунт на [Beget.com](https://beget.com)
- ✅ Токен бота от BotFather
- ✅ SSH доступ (включен по умолчанию на Beget)

---

## 🔧 Пошаговая инструкция

### Шаг 1: Подготовка файлов

Все файлы уже готовы! Вам нужно загрузить проект на сервер.

### Шаг 2: Подключение по SSH

#### Через браузер (легкий способ):
1. Войдите в [панель Beget](https://cp.beget.com)
2. Найдите раздел **"SSH/SFTP"** или **"Терминал"**
3. Нажмите **"Открыть терминал"** или **"Web SSH"**

#### Через программу (для продвинутых):
1. Скачайте [PuTTY](https://www.putty.org/) (для Windows)
2. Подключитесь к серверу:
   - Host: `ваш_логин.beget.tech`
   - Port: `22`
   - Username: ваш логин на Beget
   - Password: ваш пароль

### Шаг 3: Загрузка файлов на сервер

#### Способ 1: Через FTP (FileZilla)
1. Скачайте [FileZilla](https://filezilla-project.org/)
2. Подключитесь:
   - Хост: `ваш_логин.beget.tech`
   - Логин: ваш логин
   - Пароль: ваш пароль
   - Порт: `21`
3. Загрузите все файлы проекта в папку `/home/ваш_логин/fluoxeofers/`

#### Способ 2: Через панель Beget
1. Откройте **"Файловый менеджер"** в панели
2. Создайте папку `fluoxeofers`
3. Загрузите все файлы проекта

#### Способ 3: Через Git (рекомендуется)
```bash
# В терминале SSH выполните:
cd ~
git clone https://github.com/ваш_репозиторий/fluoxeofers.git
# Или загрузите файлы вручную
```

### Шаг 4: Установка зависимостей

В SSH терминале выполните:

```bash
# Перейдите в папку проекта
cd ~/fluoxeofers

# Создайте виртуальное окружение
python3 -m venv venv

# Активируйте виртуальное окружение
source venv/bin/activate

# Обновите pip
pip install --upgrade pip

# Установите зависимости
pip install -r requirements.txt
```

### Шаг 5: Настройка .env файла

```bash
# Создайте .env файл
nano .env

# Вставьте следующее (замените YOUR_BOT_TOKEN на реальный токен):
BOT_TOKEN=ваш_токен_от_BotFather
ALLOWED_USERS=

# Сохраните: Ctrl+O, Enter, Ctrl+X
```

### Шаг 6: Тестовый запуск

```bash
# Активируйте окружение (если не активировано)
source venv/bin/activate

# Запустите бота для теста
python bot.py
```

Если всё работает, вы увидите:
```
✅ Бот запущен и готов к работе...
```

**Нажмите Ctrl+C для остановки**

### Шаг 7: Постоянный запуск через systemd

Создайте файл сервиса:

```bash
nano ~/fluoxeofers/bot_service.sh
```

Вставьте:
```bash
#!/bin/bash
cd /home/ваш_логин/fluoxeofers
source venv/bin/activate
python bot.py
```

Замените `ваш_логин` на ваш реальный логин на Beget!

Сделайте файл исполняемым:
```bash
chmod +x ~/fluoxeofers/bot_service.sh
```

### Шаг 8: Настройка автозапуска через cron

```bash
# Откройте crontab
crontab -e

# Добавьте строку (замените ваш_логин):
@reboot /home/ваш_логин/fluoxeofers/bot_service.sh >> /home/ваш_логин/fluoxeofers/bot.log 2>&1 &

# Сохраните: Ctrl+O, Enter, Ctrl+X
```

### Шаг 9: Запуск в фоне (screen)

```bash
# Установите screen (если нет)
# На Beget обычно уже установлен

# Создайте новую сессию
screen -S telegram_bot

# Активируйте окружение
cd ~/fluoxeofers
source venv/bin/activate

# Запустите бота
python bot.py

# Отключитесь от сессии: Ctrl+A, затем D
```

Теперь бот работает в фоне!

#### Полезные команды screen:
```bash
# Посмотреть список сессий
screen -ls

# Подключиться к сессии
screen -r telegram_bot

# Остановить бота: Ctrl+C
# Выйти из screen: Ctrl+A, затем D
```

---

## 🔄 Альтернатива: Использование supervisor

Если на Beget доступен supervisor (более надежный способ):

```bash
# Создайте конфиг
nano ~/fluoxeofers/supervisor.conf
```

Содержимое:
```ini
[program:telegram_bot]
command=/home/ваш_логин/fluoxeofers/venv/bin/python /home/ваш_логин/fluoxeofers/bot.py
directory=/home/ваш_логин/fluoxeofers
user=ваш_логин
autostart=true
autorestart=true
stderr_logfile=/home/ваш_логин/fluoxeofers/error.log
stdout_logfile=/home/ваш_логин/fluoxeofers/bot.log
```

Запустите:
```bash
supervisorctl -c ~/fluoxeofers/supervisor.conf start telegram_bot
```

---

## 📊 Проверка работы бота

### 1. Проверьте процесс:
```bash
ps aux | grep bot.py
```

### 2. Посмотрите логи:
```bash
tail -f ~/fluoxeofers/bot.log
```

### 3. Проверьте в Telegram:
Напишите боту `/start` - если отвечает, всё работает! ✅

---

## 🛠️ Управление ботом

### Остановить бота:
```bash
# Если через screen
screen -r telegram_bot
# Затем Ctrl+C

# Или найдите процесс и убейте
ps aux | grep bot.py
kill -9 PID_процесса
```

### Перезапустить бота:
```bash
screen -r telegram_bot
# Ctrl+C (остановить)
python bot.py
# Ctrl+A, D (отключиться)
```

### Обновить бота:
```bash
cd ~/fluoxeofers
# Загрузите новые файлы через FTP
# Или git pull если используете Git

# Перезапустите бота
screen -r telegram_bot
# Ctrl+C
python bot.py
# Ctrl+A, D
```

---

## 📝 Просмотр логов

```bash
# Последние 50 строк
tail -n 50 ~/fluoxeofers/bot.log

# В реальном времени
tail -f ~/fluoxeofers/bot.log

# Весь лог
cat ~/fluoxeofers/bot.log
```

---

## ⚠️ Возможные проблемы и решения

### Проблема: "Permission denied"
```bash
# Дайте права на выполнение
chmod +x ~/fluoxeofers/bot_service.sh
```

### Проблема: "Module not found"
```bash
# Убедитесь что виртуальное окружение активно
source ~/fluoxeofers/venv/bin/activate

# Переустановите зависимости
pip install -r ~/fluoxeofers/requirements.txt
```

### Проблема: "Connection timeout"
```bash
# Проверьте интернет-соединение сервера
ping google.com

# Проверьте токен бота
cat ~/fluoxeofers/.env
```

### Проблема: Бот останавливается при закрытии SSH
```bash
# Используйте screen или nohup
nohup python bot.py > bot.log 2>&1 &

# Или screen (рекомендуется)
screen -S telegram_bot
python bot.py
# Ctrl+A, D
```

---

## 📱 Быстрая шпаргалка команд

```bash
# Подключение к боту
screen -r telegram_bot

# Отключение от бота (бот продолжает работать)
Ctrl+A, затем D

# Просмотр логов
tail -f ~/fluoxeofers/bot.log

# Остановка бота
screen -r telegram_bot → Ctrl+C

# Запуск бота
screen -S telegram_bot
cd ~/fluoxeofers
source venv/bin/activate
python bot.py
```

---

## 🎯 Checklist перед запуском

- [ ] Файлы загружены на сервер
- [ ] Создано виртуальное окружение
- [ ] Установлены зависимости
- [ ] Создан .env с токеном
- [ ] Протестирован запуск вручную
- [ ] Настроен автозапуск (screen/cron)
- [ ] Бот работает в фоне
- [ ] Проверено в Telegram

---

## 💡 Полезные советы

1. **Используйте screen** - это самый простой способ для начинающих
2. **Проверяйте логи** регулярно для отслеживания ошибок
3. **Делайте бэкапы** .env файла (но не публикуйте его!)
4. **Обновляйте бота** регулярно для безопасности

---

## 📞 Техподдержка Beget

Если что-то не получается:
- 📧 Email: support@beget.ru
- 💬 Онлайн-чат на сайте
- 📱 Telegram: @beget_support

---

## ✅ Готово!

Ваш бот теперь работает 24/7 на Beget! 🎉

**Важно**: Не забывайте периодически проверять логи и обновлять бота.

**Удачи с вашим NFT Offers Bot! 🎁💎⭐**
